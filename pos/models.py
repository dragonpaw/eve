from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Q
import math
import time

from ccp.models import MapDenormalize, SolarSystem, Item
from settings import logging
from lib.decorators import cachedmethod

MOON_MINERALS = [x.id for x in Item.objects.filter(group__name = 'Moon Materials')]
STRONT = Item.objects.get(name='Strontium Clathrates')
VOLUME_CACHE = {
    STRONT.id: STRONT.volume,
}

#class FuelDepot(models.Model):
#    location = models.ForeignKey('ccp.SolarSystem')
#    note = models.TextField()
#
#    def __unicode__(self):
#        if (self.note == ""):
#            return self.locaiton
#        else:
#            return u"%s (%s)" % (self.location, self.note)
#
#    class Admin:
#        list_display = ('location', 'note')

#class FuelSupply(models.Model):
#    depot = models.ForeignKey(FuelDepot)
#    type = models.ForeignKey('ccp.Item')
#    quantity = models.IntegerField()
#
#    def __unicode__(self):
#        return u"%s: %s" % (self.depot.location, self.type)
#
#    class Admin:
#        list_display = ('depot', 'type', 'quantity')
#
#    class Meta:
#        ordering = ['type']

# Create your models here.
class PlayerStation(models.Model):
    q = Q(group__name='Control Tower') & Q(published=True)

    POS_STATES = (
                  (1, 'Anchored'),
                  (2, 'Newly Anchored(?)'),
                  (3, 'Reinforced'),
                  (4, 'Online'),
    )
    YES_NO = (
              (0, 'No'),
              (1, 'Yes'),
              )

    moon = models.ForeignKey('ccp.MapDenormalize')
    solarsystem = models.ForeignKey('ccp.SolarSystem')
    constellation = models.ForeignKey('ccp.Constellation')
    region = models.ForeignKey('ccp.Region')
    tower = models.ForeignKey('ccp.Item', limit_choices_to = q)
    state = models.IntegerField(choices=POS_STATES)
    state_time = models.DateTimeField(blank=True, null=True)
    online_time = models.DateTimeField(blank=True, null=True)
    cached_until = models.DateTimeField(blank=True)
    last_updated = models.DateTimeField(blank=True)
    corporation = models.ForeignKey('ccp.Corporation', related_name='pos')

    corporation_use = models.BooleanField()
    alliance_use = models.BooleanField()
    deploy_flags = models.IntegerField(blank=True)
    usage_flags = models.IntegerField(blank=True)
    claim = models.BooleanField()

    attack_standing_value = models.FloatField()
    attack_aggression = models.BooleanField()
    attack_atwar = models.BooleanField()
    attack_secstatus_flag = models.BooleanField()
    attack_secstatus_value = models.FloatField()

    cpu_utilization = models.DecimalField(default=1, max_digits=6, decimal_places=4)
    power_utilization = models.DecimalField(default=1, max_digits=6, decimal_places=4)

    note = models.CharField(max_length=200, default='', blank=True)
    owner = models.ForeignKey('user.Character', blank=True, null=True)

    fueled_until = models.DateTimeField(blank=True, null=True)
    sov_fuel_rate = models.DecimalField(default=1, max_digits=6, decimal_places=4)
    sov_level = models.CharField(max_length=20, default='None')



    class Meta:
        ordering = ['moon']

    def __unicode__(self):
        return u"%s (%s)" % (self.moon, self.corporation)

    @property
    def cpu_percent(self):
        return int(self.cpu_utilization * 100)

    @property
    def power_percent(self):
        return int(self.power_utilization * 100)

    @property
    def is_reinforced(self):
        return self.state_name == 'Reinforced'

    @property
    def is_online(self):
        return self.state_name == 'Online'

    @property
    def name(self):
        return self.moon.name

    @property
    def state_name(self):
        return [s for s in self.POS_STATES if s[0] == self.state][0][1]
        #return self.POS_STATES[self.state]

    def get_absolute_url(self):
        return "/pos/%d/detail/" % self.id

    #def get_profit_url(self):
    #    return "/pos/%d/profit/" % self.id

    @property
    def cache_remaining(self):
        return max(self.cached_until - datetime.utcnow(), timedelta(0))

    @property
    @cachedmethod(15)
    def hours_of_fuel(self):
        x = [f.hours_of_fuel for f in self.fuel.exclude(purpose='Reinforce')
                    if f.consumption > 0]
        if len(x) == 0:
            return 0
        else:
            return min(x)

    @property
    @cachedmethod(15)
    def fuel_needed(self):
        hours = self.hours_of_fuel
        fuels = [f.type for f in self.fuel.exclude(purpose='Reinforce')
                 if f.hours_of_fuel == hours and f.consumption > 0]
        return fuels

    def update_fueled_until(self):
        if self.state_time is None:
            self.fueled_until = None
            return None

        hours = self.hours_of_fuel
        if hours == 0:
            self.fueled_until = None
        else:
            remaining = timedelta(hours=hours)
            self.fueled_until = self.state_time + remaining
        return self.fueled_until

    @property
    @cachedmethod(15)
    def time_remaining(self):
        if self.state_time is None:
            return None
        elif self.fueled_until is None:
            return None
        else:
            remaining = self.fueled_until - datetime.utcnow()
            return max(remaining, timedelta(0))

    def setup_fuel_supply(self):
        log = logging.getLogger('eve.pos.model.PlayerStation.setup_fuel_supply')
        log.debug('Invoked.')
        for f in self.tower.fuel.all():
            if f.faction:
                if f.faction != self.solarsystem.faction:
                    continue
                elif self.solarsystem.security < f.minsecuritylevel:
                    continue
            try:
                self.fuel.get(station=self, type=f.type)
                log.debug('%s: Already exists: %s', self, f)
            except FuelSupply.DoesNotExist:
                log.info('%s: Creating fuel record for type: %s', self, f)
                self.fuel.create(
                    type            = f.type,
                    quantity        = 0,
                    purpose         = f.purpose.name,
                    max_consumption = f.quantity,
                )

    @property
    def icon32(self):
        return self.tower.icon32

    def reacted_quantities(self):
        d = {}
        for r in self.reactions.all():
            for item_id, quantity in r.inputs():
                if item_id in d:
                    d[item_id]['quantity'] -= quantity
                else:
                    item = Item.objects.get(id=item_id)
                    d[item_id] = { 'quantity':-quantity, 'item':item }
            for item_id, quantity in r.output():
                if item_id in d:
                    d[item_id]['quantity'] += quantity
                else:
                    item = Item.objects.get(id=item_id)
                    d[item_id] = { 'quantity': quantity, 'item': item }
        return [(x['item'], x['quantity']) for x in d.values()]

    def refresh_needed(self):
        if self.cached_until and self.cached_until > datetime.utcnow():
            return False
        else:
            return True

    def refresh(self, record, api, corp=None, force=False):
        log = logging.getLogger('eve.pos.model.PlayerStation.refresh')
        messages = []

        try:
            moon = MapDenormalize.objects.get(id=record.moonID)
            solarsystem = SolarSystem.objects.get(id=record.locationID)
        except MapDenormalize.DoesNotExist:
            log.error('Error looking up Moon! ID: %s' % record.moonID)
            raise
        except SolarSystem.DoesNotExist:
            log.error('Error looking up SolarSystem! ID: %s' % record.locationID)
            raise
        tower = Item.objects.get(pk=record.typeID)

        if not force and not self.refresh_needed():
            messages.append("Cached: POS: %s at %s." % (tower, moon))
            return messages

        log.info('Reloading: %s' % self.id)
        messages.append("Reloading: POS: %s at %s." % (tower, moon))

        detail = api.StarbaseDetail(itemID=record.itemID)

        self.tower = tower
        self.corporation = corp
        self.moon = moon
        self.solarsystem = solarsystem
        self.constellation = self.moon.constellation
        self.region = self.moon.region

        if record.stateTimestamp > 0:
            state_time = datetime(*time.gmtime(record.stateTimestamp)[0:5])
        else:
            state_time = None
        if record.onlineTimestamp > 0:
            online_time = datetime(*time.gmtime(record.onlineTimestamp)[0:5])
        else:
            online_time = None

        hours_since_update = None
        if self.state_time and state_time:
            assert isinstance(state_time, datetime)
            assert isinstance(self.state_time, datetime)
            delta = state_time - self.state_time
            hours_since_update = (delta.seconds / 60**2) + (delta.days * 24)
            log.debug('Time then: %s, Now: %s' % (self.state_time, state_time))
            log.debug("Hours since update: %d." % hours_since_update)
            messages.append('Hours since update: %d.' % hours_since_update)

        # Setup the sov level and fuel rate.
        if self.corporation.alliance_id is None:
            # This check covers non-alliance systems without sov.
            self.sov_level = 'None'
            self.sov_fuel_rate = Decimal(1)
        elif self.corporation.alliance_id == self.constellation.alliance_id:
            self.sov_level = 'Constellation'
            self.sov_fuel_rate = Decimal('0.70')
        elif self.corporation.alliance_id == self.solarsystem.alliance_id:
            self.sov_level = 'System'
            self.sov_fuel_rate = Decimal('0.75')
        else:
            self.sov_level = 'None'
            self.sov_fuel_rate = Decimal(1)

        self.state = record.state
        self.online_time = online_time
        self.state_time = state_time

        self.corporation_use = detail.generalSettings.allowCorporationMembers == 1
        self.alliance_use = detail.generalSettings.allowAllianceMembers == 1
        self.claim = detail.generalSettings.claimSovereignty == 1
        self.usage_flags = detail.generalSettings.usageFlags
        self.deploy_flags = detail.generalSettings.deployFlags

        self.attack_aggression = detail.combatSettings.onAggression.enabled == 1
        self.attack_atwar= detail.combatSettings.onCorporationWar.enabled == 1
        self.attack_secstatus_flag = detail.combatSettings.onStatusDrop.enabled == 1
        self.attack_secstatus_value = detail.combatSettings.onStatusDrop.standing / 100.0
        self.attack_standing_value = detail.combatSettings.onStandingDrop.standing / 100.0

        self.cached_until = datetime.utcfromtimestamp(detail._meta.cachedUntil)
        self.last_updated = datetime.utcnow()

        self.save()
        self.setup_fuel_supply()

        if hours_since_update is 0 and not force:
            messages.append('Bypassing update as 0 hours elapsed, so avoid CCP bug with StationDetaiil API.')
            return messages
        elif hours_since_update is None:
            log.debug('Either the tower is new, or offline or something. Updating.')
            messages.append('Unable to compute last update. Forcing refresh.')

        # Now, the fuel.
        for fuel_type in detail.fuel:
            log.debug("Fuel type: %s", fuel_type)
            type = Item.objects.get(id=fuel_type.typeID)
            try:
                fuel = self.fuel.get(type=type)
            except FuelSupply.DoesNotExist:
                messages.append('POS fuel "%s" is loaded in tower, but not a used type for this POS.' % type)
                log.info('%s: Un-needed fuel loaded: %s', self, type)
                continue

            purpose = fuel.purpose
            messages.append(' %s (%s): %s -> %s' % (type.name, purpose, fuel.quantity, fuel_type.quantity) )
            log.info('%s: %s (%s): %s -> %s (%s hours)' % (self.id, type.name, purpose, fuel.quantity, fuel_type.quantity, hours_since_update) )

            #if purpose in (u'CPU', u'Power'):
            #    log.debug('Matched cpu/power test.')
            #if hours_since_update > 0:
            #    log.debug('Matched hours > 0 test.')
            if purpose in ('CPU', 'Power') and hours_since_update > 0:
                log.debug('Recalculating consumption.')
                consumed = (fuel.quantity - fuel_type.quantity) / hours_since_update
                max = Decimal(fuel.max_consumption * self.sov_fuel_rate)
                log.debug('Consumed: %s units.' % consumed)
                if consumed < 0:
                    continue
                if consumed > max:
                    continue

                if purpose == 'CPU':
                    self.cpu_utilization = consumed / max
                    messages.append("  Calculated: CPU Utilization: %d%%" % self.cpu_percent)
                    log.info('%s: CPU Util: %0.2f' % (self.id, self.cpu_utilization))
                else:
                    self.power_utilization = consumed / max
                    messages.append("  Calculated: Power Utilization: %d%%" % self.power_percent)
                    log.info('%s: Power Util: %0.2f' % (self.id, self.power_utilization))

            fuel.quantity=fuel_type.quantity
            fuel.save()

        # Once all fuel is loaded, calculate how much runtime that gives us.
        until = self.update_fueled_until()
        messages.append('Fueled until: %s' % until)
        self.save()

        return messages

#class PlayerStationModule(models.Model):
#    q = Q(group__category__name='Structure', published=True) & ~Q(group__name='Control Tower')
#
#    item = models.ForeignKey('ccp.Item', limit_choices_to = q)
#    station = models.ForeignKey(PlayerStation)
#    online = models.BooleanField(default=True)
#
#    def __unicode__(self):
#        return u"%s" % (self.item)
#
#class PlayerStationDelegation(models.Model):
#    station = models.ForeignKey(PlayerStation, related_name='delegates')
#    character = models.ForeignKey('user.Character', related_name='pos_delegations')

class FuelSupply(models.Model):
    station = models.ForeignKey(PlayerStation, related_name='fuel')
    type = models.ForeignKey('ccp.Item', related_name='active_stations_using')
    quantity = models.IntegerField(default=0)
    max_consumption = models.IntegerField(default=0)
    purpose = models.CharField(max_length=10, default='Online')
    #solarsystem = models.ForeignKey('ccp.SolarSystem')
    #constellation = models.ForeignKey('ccp.Constellation')
    #region = models.ForeignKey('ccp.Region')
    #corporation = models.ForeignKey('ccp.Corporation', related_name='pos_fuels')

    class Meta:
        ordering = ['type']
        unique_together = (('station', 'type'),)

    def __unicode__(self):
        return u"%s: %s (%d)" % (self.station, self.type, self.quantity)

    @property
    @cachedmethod(60)
    def fuel_info(self):
        fuel_info = self.station.tower.fuel.get(type=self.type)
        return fuel_info

    #@property
    #@cachedmethod(60)
    #def _purpose(self):
    #    return self.fuel_info.purpose.name

    #@property
    #@cachedmethod(5)
    #def max_consumption(self):
    #    fuel_info = self.fuel_info
    #    burn_rate = int(fuel_info.quantity)
    #    if fuel_info.purpose != 'Reinforce':
    #        burn_rate = math.ceil(burn_rate * self.station.sov_fuel_rate)
    #
    #    return int(burn_rate)

    @property
    @cachedmethod(5)
    def consumption(self):
        purpose = self.purpose
        if purpose == 'Reinforce':
            rate = self.max_consumption
        else:
            rate = self.max_consumption * self.station.sov_fuel_rate

        if purpose == 'Power':
            rate = rate * self.station.power_utilization
        elif purpose == 'CPU':
            rate = rate * self.station.cpu_utilization

        return int(math.ceil(rate))

    def goal(self, days):
        # The goal of stront is always to be full.
        if self.purpose == 'Reinforce':
            attrib = self.station.tower.attribute_by_name('capacitySecondary')
            max_volume = attrib.value
            need = int(max_volume / VOLUME_CACHE[self.type_id])
            return need
        else:
            return self.consumption * 24 * days

    def need(self, days):
        need = self.goal(days) - self.quantity
        return max(need, 0)

    @property
    def hours_of_fuel(self):
        if self.consumption == 0:
            return 0
        else:
            return int(self.quantity / self.consumption)

    @property
    def time_remaining(self):
        if self.station.state_time is None:
            return None

        remaining = timedelta(hours=self.hours_of_fuel)
        #remaining = max(remaining, 0) # Don't show negative values.
        now = datetime.utcnow()

        if self.purpose == 'Reinforce':
            if self.station.is_reinforced:
                remaining = self.station.state_time - now
                return max(remaining, timedelta(0))
            else:
                return remaining
        else:
            remaining += (self.station.state_time - now)
            return max(remaining, timedelta(0))

    @property
    def runs_until(self):
        return datetime.utcnow() + self.time_remaining

class Reaction(models.Model):
    '''
    All of the items that can be mined and/or reacted at a POS.

    This includes moon mining, basic reactions, and advanced reactions.
    '''

    #q = Q(group__name__in=['Moon Materials', 'Intermediate Materials',
    #                       'Composite'])
    q = Q(group__name__in=['Moon Materials','Simple Reaction','Complex Reactions'])
    q = q & Q(published=True)

    station = models.ForeignKey(PlayerStation, related_name='reactions')
    type = models.ForeignKey('ccp.Item', limit_choices_to = q,
                             related_name='poses_reacting')

    class Meta:
        ordering = ['type']

    def __unicode__(self):
        return u"%s: %s" % (self.station, self.type)

    def get_absolute_url(self):
        return self.type.get_absolute_url()

    @property
    def name(self):
        return self.type.name

    @property
    def note(self):
        if self.is_mining:
            return u'Mining'
        else:
            return u'Reacting'

    def get_icon(self, size):
        return self.type.get_icon(size)

    @property
    def icon32(self):
        return self.get_icon(32)

    @property
    def is_mining(self):
        return self.type_id in MOON_MINERALS

    @property
    def is_reaction(self):
        return not self.is_mining

    #@property
    #@cachedmethod(60)
    #def reaction(self):
    #    if self.is_mining:
    #        return None
    #    else:
    #        return self.type.reacts.filter(input=False)[0].reaction

    @cachedmethod(60)
    def inputs(self):
        '''
        Return a tuple of (item_id, quantity) for all items consumed by this
        reaction.
        '''
        if self.is_mining:
            return []
        else:
            inputs = self.type.reactions.filter(input=True)
            return [ (i.item_id, i.quantity) for i in inputs ]

    @cachedmethod(60)
    def output(self):
        '''
        Return a tuple of (item_id, quantity) for what this reacton outputs.
        '''

        if self.is_mining:
            return [ (self.type.id, 100) ]
        else:
            outputs = self.type.reactions.filter(input=False)
            return [ (i.item_id, i.quantity) for i in outputs ]
