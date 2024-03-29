from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timedelta
import time
import pickle
import socket
import logging

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import models
from django.db.models.signals import post_save

from eve.lib import eveapi
from eve.lib.jfilters import filter_comma as comma
from eve.trade.models import Transaction, JournalEntry, MarketIndexValue, MarketIndex
from eve.pos.models import PlayerStation
from eve.lib.decorators import cachedmethod
from eve.ccp.models import Item

API = eveapi.get_api()

#CHARACTER_CACHE_TIME = timedelta(hours=1)
TRANSACTION_CUTOFF = timedelta(days=30)
STALE_ACCOUNT = timedelta(days=14)
ACCOUNT_LOST_EXPIRATION = timedelta(days=1)

ITEM_SKILLS = {'group__category__name__exact': 'Skill'}

class UserProfile(models.Model):
    '''
    A profile to extend the built-in Django User class.

    # Create a user.
    >>> user = User(username='test', email='ash-test@dragonpaw.org')
    >>> user.save()
    >>> user.username
    'test'

    # Should have an ID now.
    >>> user.id is None
    False

    # And it should have automatically made a profile
    >>> profile = user.get_profile()
    >>> profile.id is None
    False
    '''

    user = models.ForeignKey(User, unique=True)
    pos_days = models.IntegerField("Days of POS fuel desired", default=30)
    pos_shipping_cost = models.DecimalField("ISK per m3 to assume for freight",
                                            max_digits=10, decimal_places=2,
                                            default=0)
    lost_password_key = models.CharField(max_length=50, blank=True)
    lost_password_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('user',)

    def __unicode__(self):
        return self.user.username

    @property
    def username(self):
        return self.user.username

    @property
    def is_stale(self):
        return self.user.last_login < (datetime.utcnow() - STALE_ACCOUNT)

    def is_lost_password_expired(self):
        return self.lost_password_time + ACCOUNT_LOST_EXPIRATION < datetime.utcnow()

    def lost_password(self):
        '''Setup the account for password recovery.'''

        # Already setup.
        if self.lost_password_key and not self.is_lost_password_expired():
            self.send_lost_password()
            return

        while True:
            key = User.objects.make_random_password(50)
            try:
                UserProfile.objects.get(lost_password_key=key)
            except UserProfile.DoesNotExist:
                self.lost_password_key = key
                self.lost_password_time = datetime.utcnow()
                self.save()
                self.send_lost_password()
                return

    def send_lost_password(self):
        self.email('user_password_lost.txt', subject='Password recovery link')

    def email(self, template, subject=None, account=None):
        if not self.user.email:
            logging.getLogger('user.model.UserProfile.email').error('%s: User has no email address set, so mail surpressed', self)
            return

        d = {}
        if account:
            d['account'] = account
        d['profile'] = self
        d['user'] = self.user

        if subject:
            subject = "EVE Magic Widget: " + subject + "."
        else:
            subject = "EVE Magic Widget"

        body = render_to_string(template, d)
        self.user.email_user(subject, body)

    def max_skill_level(self, name):
        q = SkillLevel.objects.filter(
                            character__account__user__exact=self,
                            skill__name = name,
                          ).order_by('-level')
        if q.count():
            return q[0].level
        else:
            return 0

    def trade_transactions(self, item=None, days=None):
        transactions = Transaction.objects.filter(character__account__user=self)
        if item:
            transactions = transactions.filter(item=item)
        if days:
            target = datetime.now() - timedelta(days)
            transactions = transactions.filter(time__gte=target)
        return transactions

    def journal_entries(self, days=None, is_boring=True):
        transactions = JournalEntry.objects.filter(character__account__user=self)
        if is_boring is False:
            boring = Q(type__is_boring=False)
            transactions = transactions.filter(boring)
        if days:
            target = datetime.now() - timedelta(days)
            transactions = transactions.filter(time__gte=target)
        return transactions

    def get_indexes(self, type):
        q = (Q(index__user__isnull=True) | Q(index__user=self)) & Q(item=type)
        indexes = MarketIndexValue.objects.filter(q)
        indexes = indexes.order_by('-trade_marketindex.priority')
        return indexes

    @cachedmethod(15)
    def get_buy_price(self, type):
        indexes = self.get_indexes(type).filter(buy__gt=0)

        if indexes.count() > 0:
            return indexes[0].buy
        else:
            return None

    @cachedmethod(15)
    def get_sell_price(self, type):
        indexes = self.get_indexes(type).filter(sell__gt=0)

        if indexes.count() > 0:
            return indexes[0].sell
        else:
            return None

    def update_personal_index(self):
        index = MarketIndex.objects.get(name="Personal Trade History",
                                        user=self)
        items = {}
        for t in Transaction.objects.filter(character__account__user=self):
            id = t.item_id
            quantity = Decimal(t.quantity)
            price = Decimal("%0.2f" % t.price)
            if not items.has_key(id):
                items[id] = {'type':t.item, 'buy':0, 'sell':0, 'buy_qty':0, 'sell_qty':0}
            if t.sold:
                items[id]['sell'] += quantity * price
                items[id]['sell_qty'] += quantity
            else:
                items[id]['buy'] += quantity * price
                items[id]['buy_qty'] += quantity
        for v in items.values():
            if v['sell_qty']:
                v['sell'] /= v['sell_qty']
            if v['buy_qty']:
                v['buy'] /= v['buy_qty']
            index.set_value(v['type'], buy=v['buy'], sell=v['sell'],
                            buy_qty=v['buy_qty'], sell_qty=v['sell_qty'])
        index.items.exclude( item__id__in=items.keys() ).delete()

    #-------------------------------------------------------------------------
    # Market transactions. (Need to add user-specific code.)
    def trade_history(self, item=None, days=None):
        transactions = self.trade_transactions(item=item, days=days)
        quantity = Decimal(0)
        avg = {}
        total = Decimal(0)

        for t in transactions:
            quantity = Decimal(t.quantity)
            price = Decimal("%0.2f" % t.price)
            region = t.region.name

            if not avg.has_key(t.region.name):
                avg[region] = {
                                    'sell_price':  0,
                                    'sell_volume': 0,
                                    'sell_total':  0,
                                    'buy_price':   0,
                                    'buy_volume':  0,
                                    'buy_total':   0,
                                    'profit_isk':  0,
                                    'profit_pct':  0,
                                    'region':      t.region
                                    }

            if t.sold:
                avg[region]['sell_volume'] += quantity
                avg[region]['sell_total'] += quantity*price
            else:
                avg[region]['buy_volume'] += quantity
                avg[region]['buy_total'] += quantity*price

        best = {'buy':None, 'sell':None}
        for v in avg.values():
            if v['sell_volume']:
                v['sell_price'] = v['sell_total'] / v['sell_volume']
            if v['buy_volume']:
                v['buy_price'] = v['buy_total'] / v['buy_volume']
            v['gross'] = v['sell_total'] - v['buy_total']
            total += v['gross']

            if v['buy_price'] and v['sell_price']:
                v['profit_isk'] = v['sell_price'] - v['buy_price']
                v['profit_pct'] = (v['profit_isk'] / v['buy_price'])*100

            if best['buy'] is None or (v['buy_volume'] > 0 and v['buy_price'] < best['buy']['buy_price']):
                best['buy'] = v

            if best['sell'] is None or (v['sell_volume'] > 0 and v['sell_price'] > best['sell']['sell_price']):
                best['sell'] = v

        if best['buy'] and best['buy']['buy_price'] and best['sell'] and best['sell']['sell_price']:
            profit_isk = best['sell']['sell_price'] - best['buy']['buy_price']
            profit_pct = (profit_isk / best['buy']['buy_price']) * 100
            best['profit_isk'] = profit_isk
            best['profit_pct'] = profit_pct
        best['gross'] = total

        return avg, best

def create_profile_for_user(sender, instance, created, **kwargs):
    try:
        UserProfile.objects.get(user=instance)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=instance
        )
        MarketIndex.objects.create(
            name     = 'Custom Prices',
            user     = profile,
            priority = 500,
            note     = 'Prices that you explicitly set.',
        )
        MarketIndex.objects.create(
            name     = 'Personal Trade History',
            user     = profile,
            priority = 400,
            note     = 'Prices based on transactions from all of your characters.',
        )

post_save.connect(create_profile_for_user, sender=User)

class Account(models.Model):
    id = models.IntegerField('ID', primary_key=True)
    user = models.ForeignKey(UserProfile, related_name='accounts')
    api_key = models.CharField(max_length=200)
    last_refreshed = models.DateTimeField(null=True, blank=True)
    refresh_messages = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('user',)

    def __unicode__(self):
        return u"%s: %s" % (self.user.username, self.id)

    @property
    def api_key_short(self):
        return self.api_key[0:4] + "..." + self.api_key[-5:-1]

    def get_absolute_url(self):
        return "/user/account/%d/" % self.id

    def get_refresh_url(self):
        return "/user/account/%d/refresh/" % self.id

    def get_refresh_warning_url(self):
        return "/user/account/%d/refreshing/" % self.id

    def get_log_url(self):
        return "/user/account/%d/api-log/" % self.id

    def get_edit_url(self):
        return "/user/account/%d/edit/" % self.id

    @property
    def name(self):
        if self.id:
            return 'Account: %d' % self.id
        else:
            return 'Account'

    def last_refreshed_delta(self):
        if self.last_refreshed:
          return datetime.utcnow() - self.last_refreshed
        else:
          return None

    def refresh_messages_list(self):
        if self.refresh_messages:
            return pickle.loads(str(self.refresh_messages))
        else:
            return []

    def api_auth(self):
        auth = API.auth(userID=self.id, apiKey=self.api_key)
        return auth

    def refresh(self, force=False):
        log = logging.getLogger('eve.user.models.Account.refresh')
        auth = self.api_auth()

        m = defaultdict(list)
        log.debug('Refreshing: %s', self)

        if self.user.is_stale and not force:
            m['Account'].append('This account has not been accessed recently, so refresh is disabled.')
            log.debug('This account has not been accessed recently, so refresh is disabled.')
            return m

        try:
            result = auth.account.Characters()

            ids = []
            for c in result.characters:
                ids.append(c.characterID)

                try:
                    character = Character.objects.get(id = c.characterID)
                except Character.DoesNotExist:
                    character = Character(id=c.characterID)
                character.account = self
                character.user=self.user

                # Name might not be set yet.
                log.info("%s: Account: %s", self, character)
                temp = character.refresh(force=force)
                log.debug(temp)
                m[character.name] = temp
                m['Account'].append('Account has character: %s' % character.name)


            # Look for deleted characters.
            for character in Character.objects.filter(account__id=self.id).exclude(id__in=ids):
                m['Account'].append("Lost character: %s will be purged." % character.name)
                log.info('%s: Character no longer exists. Deleted.', character)
                character.delete()

        except eveapi.Error, e:
            msg = str(e)
            if msg in ('Authentication failure',
                          'Invalid accountKey provided',
                          'Failed getting user information',
                          'Cached API key authentication failure'):
                m['Account'].append("This account has an invalid API key. Deleted.")
                log.warn("%s: This account has an invalid API key. Deleted.", self)
                self.email('user_invalid_api_key.txt', subject='Invalid API key')
                self.delete()
                return m
            elif msg == 'Current security level not high enough':
                self.email('user_wrong_api_key.txt', subject='Wrong API key used')
                m['Account'].append("Deleted account '%s', user gave limited key." % self.id)
                log.warn("%s: User gave limited key. Deleted.", self)
                self.delete()
                return m
            elif msg == 'Login denied by account status':
                m['Account'].append("This accout shows as suspended.")
                log.warn('%s: Account is no longer active', self)
            elif msg == 'EVE backend database temporarily disabled':
                m['Account'].append('The EVE API has been taken offline by CCP.')
                log.warn('EVE API disabled.')
            elif msg == 'Unexpected failure accessing database':
                m['Account'].append('EVE API gave unexpected error')
                log.warn('EVE API gave unexpected error.')
            else:
                m['Account'].append('EVE API error: %s' % msg)
                log.exception('%s: EVE API error: %s', self, msg)
        except socket.error, e:
            msg = str(e)
            if 'Connection reset by peer' in msg:
                log.warn('Connection reset on EVE API call.')
            elif 'Connection refused' in msg:
                m['Account'].append('EVE API server is not accepting connections.')
                log.warn('EVE API server: connection refused.')
            else:
                m['Account'].append('EVE API error(socket): %s' % e)
                log.error('%s: EVE API error(socket): %s', self, e)

        self.refresh_messages = pickle.dumps(m['Account'])
        self.last_refreshed = datetime.now()
        self.save()
        log.debug('%s: Done.', self)
        return m

    def email(self, template, subject=None):
        return self.user.email(template, subject=subject, account=self)

class Character(models.Model):
    id = models.IntegerField('ID', primary_key=True)
    account = models.ForeignKey(Account, related_name='characters')
    name = models.CharField(max_length=100)
    isk = models.FloatField(null=True, blank=True)
    #training_completion = models.DateTimeField(null=True, blank=True)
    #training_level = models.IntegerField(null=True, blank=True)
    #training_skill = models.ForeignKey('ccp.Item', null=True, blank=True,
    #                 limit_choices_to = {'group__category__name': 'Skill', 'published': True})
    is_director = models.BooleanField('Has Director role', default=False)
    is_pos_monkey = models.BooleanField('Has POS Caretaker role', default=False)
    corporation = models.ForeignKey('ccp.Corporation', related_name='characters')
    user = models.ForeignKey(UserProfile, related_name='characters')
    last_refreshed = models.DateTimeField(blank=True)
    cached_until = models.DateTimeField(blank=True)
    refresh_messages = models.TextField(default='')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/user/character/%d/" % self.id

    def save( self, *args, **kwargs ):
        messages = []
        try:
            old = Character.objects.get( pk = self._get_pk_val() )
            if self.corporation_id != old.corporation_id:
                messages.append("Corporation changed. Purging delegations and rights.")
                #self.pos_delegations.all().delete()
        except Character.DoesNotExist:
            pass
        super( Character, self ).save(*args, **kwargs)

        return messages

    def refresh_messages_list(self):
        if self.refresh_messages:
            return pickle.loads(str(self.refresh_messages))
        else:
            return []

    def get_icon(self, size):
        # CCP gives us only two sizes.
        if size in (64, 256):
            return "http://img.eve.is/serv.asp?s=%d&c=%s" % (size, self.id)
        else:
            return None

    @property
    def icon64(self):
        return self.get_icon(64)

    @property
    def icon256(self):
        return self.get_icon(256)

    def last_refreshed_delta(self):
        return datetime.utcnow() - self.last_refreshed

    def cache_remaining(self):
        now = datetime.utcnow()
        if self.cached_until < now:
            return None
        else:
            return self.cached_until - now


    @property
    def skill_points(self):
        total = 0
        for s in self.skills.all():
            total += s.points

        return total

    def get_isk_formatted(self):
        return comma(self.isk)+' ISK'
    isk_formatted = property(get_isk_formatted)
    get_isk_formatted.short_description = "ISK"

    def get_sp_formatted(self):
        return comma( self.skill_points )
    skill_points_formatted = property(get_sp_formatted)
    get_sp_formatted.short_description = "Skill Points"

    @property
    def is_training(self):
        return datetime.utcnow() <= self.training_completion

    @property
    def training_remaining(self):
        if self.is_training:
            return self.training_completion - datetime.utcnow()
        else:
            return None

    def api_character(self):
        auth = self.account.api_auth()
        auth = auth.character(self.id)
        return auth

    def api_corporation(self):
        auth = self.account.api_auth()
        auth = auth.corporation(self.id)
        return auth

    def refresh(self, force=False):
        messages = []

        messages.extend( self.refresh_character(force=force) )

        #if self.is_director:
        #    messages.extend( self.refresh_poses(force=force) )

        return messages

    def refresh_character(self, force=False):
        from eve.ccp.models import Corporation

        messages = []
        if not force and self.cached_until and self.cached_until > datetime.utcnow():
            messages.append("Character: %s (%d): Still cached." % (self.name, self.id))
            return messages

        api = self.api_character()

        character_sheet = api.CharacterSheet()
        self.name = character_sheet.name
        try:
            corporation = Corporation.objects.get(pk=character_sheet.corporationID)
        except Corporation.DoesNotExist:
            corporation = Corporation(id=character_sheet.corporationID)
        messages.extend( corporation.refresh(character=self, name=character_sheet.corporationName) )
        self.corporation = corporation

        messages.append("Starting Character: %s (%d)" % (self.name, self.id))

        # We set the account earlier in update_account. Now just make sure it matches.
        # Usernames can not change, but a character might move between accounts.
        self.user = self.account.user
        self.last_refreshed = datetime.utcnow()
        self.cached_until = datetime.utcfromtimestamp(character_sheet._meta.cachedUntil)

        self.is_director = False
        self.is_pos_monkey = False
        for role in character_sheet.corporationRoles:
            if role.roleName == 'roleStarbaseCaretaker':
                self.is_pos_monkey = True
            elif role.roleName == 'roleDirector':
                self.is_director = True
        messages.append('Is director?: %s' % self.is_director)
        messages.append('Is POS caretaker?: %s' % self.is_pos_monkey)

        self.save()

        messages.extend( self.refresh_wallet() )
        messages.extend( self.refresh_skills() )
        messages.extend( self.refresh_journal() )

        msg, new = self.refresh_transactions()
        messages.extend( msg )

        msg, purged = self.purge_old_data()
        messages.extend( msg )

        if purged or new:
            self.user.update_personal_index()
            messages.append('Transactions changed, updated personal index.')

        self.refresh_messages = pickle.dumps(messages)
        messages.extend( self.save() )

        return messages

    def refresh_wallet(self):
        me = self.api_character()

        wallet = me.AccountBalance()
        self.isk = wallet.accounts[0].balance
        self.save()
        return ['Wallet balance: %s ISK' % comma(self.isk)]

    def refresh_skills(self):
        log = logging.getLogger('eve.user.models.Character.refresh_skills')

        me = self.api_character()
        skills = 0
        points = 0
        messages = []

        # Easier to just wipe the queue and re-create each time.
        SkillInTraining.objects.filter(character=self).delete()
        for s in me.SkillQueue().skillqueue:
            skill = Item.objects.get(pk=s.typeID)
            if s.endTime:
                t = datetime.fromtimestamp(s.endTime)
            else:
                t = None
            queued = self.skills_in_queue.create(
                skill = skill,
                level = s.level,
                order = s.queuePosition,
                finish_time = t,
            )

            messages.append('Training: %s %s' % (
                    queued.skill, queued.level
            ))
            log.debug('%s: Now training: %s %s',
                      self, queued.skill, queued.level)

        sheet = me.CharacterSheet()
        for row in sheet.skills:
            skills += 1
            points += row.skillpoints

            try:
                skill = Item.objects.get(pk=row.typeID)
            except Item.DoesNotExist:
                log.warn('%s: Has a non-existant skill: ID=%s', self, row.typeID)
                continue
            obj, _ = self.skills.get_or_create(skill=skill)

            if obj.points != row.skillpoints or obj.level != row.level:
                obj.points = row.skillpoints
                obj.level = row.level
                obj.save()

        messages.append('Skills: %d, Total SP: %0.2fm' % (skills, points/1000000.0))
        return messages

    def refresh_transactions(self):
        me = self.api_character()
        messages = []

        last_id = 0
        stopping_time = time.time() - (60*60*24*7)
        qty = 0
        wallet = None
        last_time = time.time()
        try:
            while qty==0 or (len(wallet.transactions) == 1000 and last_time > stopping_time):
                if last_id == 0:
                    #m.append("Loading first wallet.")
                    wallet = me.WalletTransactions()
                else:
                    #m.append("Loading wallet before %d" % last_id)
                    wallet = me.WalletTransactions(beforeTransID=last_id)
                for t in wallet.transactions:
                    try:
                        self.transactions.get(character = self,
                                              transaction_id = t.transactionID)
                        messages.append("Loaded %d new transactions." % qty)
                        return messages, qty
                    except Transaction.DoesNotExist:
                        pass

                    messages.extend( self.update_transactions_single(t) )
                    last_id = t.transactionID
                    last_time = t.transactionDateTime
                    qty+=1
                if last_id == 0:
                    messages.append("No transactions to load.")
                    return messages, qty
                else:
                    messages.append("Loaded %d new transactions." % qty)
                    return messages, qty
        except eveapi.Error, e:
            msg = str(e)
            messages.append(msg)
            if 'Wallet exhausted' in msg:
                pass
            elif 'Expected before ref/trans ID' in msg:
                pass
            elif 'Already returned one week of data:' in msg:
                pass
            else:
                raise

            return messages, qty

    def update_transactions_single(self, t):
        from eve.ccp.models import Item, Station

        if t.transactionType == 'buy':
            sold = False
        else:
            sold = True

        try:
            item = Item.objects.get(pk=t.typeID)
        except Item.DoesNotExist:
            return ["ERROR: Type ID: '%s' not found in DB." % t.typeID]

        try:
            station = Station.objects.get(id=t.stationID)
        except Station.DoesNotExist:
            return ["ERROR: Station ID: '%s' not found in DB." % t.stationID]

        obj = Transaction(character = self,
                          transaction_id = t.transactionID,
                          sold = sold,
                          item = item,
                          price = t.price,
                          quantity = t.quantity,
                          station =  station,
                          region = station.region,
                          time = datetime(*time.gmtime(t.transactionDateTime)[0:5]),
                          client = t.clientName,
                          )
        obj.save()
        return ['Transaction: %s x %s: %s ISK' % (obj.quantity, obj.item, obj.price*obj.quantity) ]

    def refresh_journal(self):
        me = self.api_character()
        messages = []
        qty = 0

        try:
            result = me.WalletJournal()
            for t in result.entries:
                if t.amount == 0:
                    continue

                id = t.refID

                try:
                    self.journal.get(character = self, transaction_id = id)
                    break
                except JournalEntry.DoesNotExist:
                    pass

                type = t.refTypeID
                amount = t.amount
                transaction_time = datetime(*time.gmtime(t.date)[0:5])
                if amount < 0:
                    client = t.ownerName2
                else:
                    client = t.ownerName1
                reason = t.reason
                amount = Decimal("%f" % amount)
                x = self.journal.create(transaction_id=id, time=transaction_time, client=client,
                                        price=amount, type_id=type, reason=reason)
                x.save()
                qty += 1

            if qty == 0:
                messages.append("No journal entries to load.")
            else:
                messages.append('Loaded %d new journal entries.' % qty)
            return messages
        except eveapi.Error, e:
            msg = str(e)
            if 'Wallet exhausted' in msg or 'Already returned one week of data' in msg:
                messages.append(msg)
                return messages
            elif 'wallet previously loaded' in msg:
                messages.append('Wallet already loaded by another API process.')
                return messages
            else:
                raise

    def purge_old_data(self):
        messages = []
        cutoff = datetime.utcnow() - TRANSACTION_CUTOFF
        old_transactions = self.transactions.filter(time__lt=cutoff)
        old_transaction_count = old_transactions.count()
        if old_transaction_count > 0:
            old_transactions.delete()
            messages.append('Deleting old transactions: %d removed.' % old_transaction_count)

        old = self.journal.filter(time__lt=cutoff)
        old_count = old.count()
        if old_count > 0:
            old.delete()
            messages.append('Deleting old journal entries: %d removed.' % old_count)

        return messages, old_transaction_count


class SkillLevel(models.Model):
    character = models.ForeignKey(Character, related_name='skills')
    skill = models.ForeignKey('ccp.Item', limit_choices_to = ITEM_SKILLS)
    level = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        ordering = ('character', 'skill')
        unique_together = (('character', 'skill'),)

    def __unicode__(self):
        return u"%s: %s" % (self.skill.name, self.level)


class SkillInTraining(models.Model):
    character = models.ForeignKey(Character, related_name='skills_in_queue')
    skill = models.ForeignKey('ccp.Item', limit_choices_to = ITEM_SKILLS)
    level = models.IntegerField()
    order = models.IntegerField()
    finish_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return u"%s: %s" % (self.skill.name, self.level)

    @property
    def remaining(self):
        if self.finish_time:
            return self.finish_time - datetime.utcnow()
        else:
            return None
