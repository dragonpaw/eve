from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth.models import User 
from django.db import models
from eve.ccp.models import Item, Corporation
from eve.util.formatting import comma
from django.db.models import signals
from django.dispatch import dispatcher

class UserProfile(models.Model):
    #url = models.URLField() 
    #home_address = models.TextField() 
    #phone_numer = models.PhoneNumberField() 
    user = models.ForeignKey(User, unique=True)

    class Meta:
        ordering = ('user',)

    class Admin:
        list_display = ('user',)
    
    def __str__(self):
        return self.user.username
    
    @property
    def username(self):
        return self.user.username
    
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
        from eve.trade.models import Transaction
        transactions = Transaction.objects.filter(character__account__user__exact=self)
        if item:
            transactions = transactions.filter(item=item)
        if days:
            target = datetime.now() - timedelta(days)
            transactions = transactions.filter(time__gte=target)
        return transactions
        
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
       
def create_profile_for_user(sender, instance, signal, *args, **kwargs):
    UserProfile.objects.get_or_create(user=instance)

dispatcher.connect(create_profile_for_user, signal=signals.post_save, sender=User)
       
class Account(models.Model):
    id = models.IntegerField(primary_key=True, core=True)
    user = models.ForeignKey(UserProfile, related_name='accounts',
                             edit_inline = models.TABULAR)
    api_key = models.CharField(max_length=200)
    last_refreshed = models.DateTimeField(null=True, blank=True)

    class Admin:
        list_display = ('user', 'id')
        list_display_links = ('id', )
        
    class Meta:
        ordering = ('user',)
        
    def __str__(self):
        return "%s: %s" % (self.user.username, self.id)
       
    @property
    def api_key_short(self):
        return self.api_key[0:4] + "..." + self.api_key[-5:-1]
    
    def get_absolute_url(self):
        return "/user/account/%d/" % self.id
    
    @property
    def name(self):
        return 'Account: %d' % self.id
        
class Character(models.Model):
    id = models.IntegerField(primary_key=True, core=True)
    account = models.ForeignKey(Account, related_name='characters',
                                edit_inline = models.TABULAR)
    name = models.CharField(max_length=100)
    isk = models.FloatField(null=True, blank=True)
    training_completion = models.DateTimeField(null=True, blank=True)
    training_level = models.IntegerField(null=True, blank=True)
    training_skill = models.ForeignKey(Item, null=True, blank=True,
                     limit_choices_to = {'group__category__name': 'Skill'})
    is_director = models.BooleanField(default=False)
    corporation = models.ForeignKey(Corporation)
    user = models.ForeignKey(UserProfile, related_name='characters')
    last_updated = models.DateTimeField(blank=True)
    cached_until = models.DateTimeField(blank=True)
    
    class Admin:
        list_display = ('name', 'user', 'get_isk_formatted', 
                        'get_sp_formatted', 'training_skill', 'training_level')

    class Meta:
        ordering = ('name',)
        
    def __str__(self):
        return self.name
        
    def icon(self, size):
        return "http://img.eve.is/serv.asp?s=%d&c=%s" % (size, self.id)
        
    @property
    def icon64(self):
        return self.icon(64)
    
    @property
    def icon256(self):
        return self.icon(256)
        
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
    
    #--------------------------------------------------------------------------
    #@property
    #def materials(self, item):
        # FIXME: This isn't the right formula actually. Not always 10% waste.
        #pe = self.skills.get(skill__name__exact='Production Efficiency').level
        # round($base_qty*(1+(0.1/(1+$mineral_level)))*(1.25-(0.05*$prod_eff_skill)))
        
    @property
    def is_training(self):
        return datetime.utcnow() <= self.training_completion
    
    @property
    def training_remaining(self):
        if self.is_training:
            return self.training_completion - datetime.utcnow()
        else:
            return None
        
    def get_absolute_url(self):
        return "/user/character/%d/" % self.id
        
class SkillLevel(models.Model):
    character = models.ForeignKey(Character, related_name='skills')
    skill = models.ForeignKey(Item,
              limit_choices_to = {'group__category__name__exact': 'Skill'})
    level = models.IntegerField()
    points = models.IntegerField()
    
    class Admin:
        search_fields = ('character__name',)
        list_display = ('character', 'skill', 'level')
        list_display_links = ('skill',)
        
    class Meta:
        ordering = ('character', 'skill')
    
    def __str__(self):
        return self.skill.name
