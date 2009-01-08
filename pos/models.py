from django.db import models
from django.db.models import Q

from datetime import datetime, timedelta
from decimal import Decimal
import math
import time

from eve.ccp.models import MapDenormalize, SolarSystem, Item

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

    note = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey('user.Character', blank=True, null=True)

    fueled_until = models.DateTimeField(blank=True, null=True)

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

    def get_absolute_url(self):
        return "/pos/%d/fuel/" % self.id

    def get_profit_url(self):
        return "/pos/%d/profit/" % self.id

    @property
    def cache_remaining(self):
        return max(self.cached_until - datetime.utcnow(), timedelta(0))

    @property
    def hours_of_fuel(self):
        x = [f.hours_of_fuel for f in self.fuel.exclude(type__name='Strontium Clathrates')
                    if f.consumption > 0]
        if len(x) == 0:
            return 0
        else:
            return min(x)

    @property
    def fuel_needed(self):
        hours = self.hours_of_fuel
        fuels = [f.type for f in self.fuel.exclude(type__name='Strontium Clathrates')
                 if f.hours_of_fuel == hours and f.consumption > 0]
        return fuels

    def update_fueled_until(self):
        if self.state_time is None:
            self.fueled_until = None
            return

        hours = self.hours_of_fuel
        if hours == 0:
            self.fueled_until = None
        else:
            remaining = timedelta(hours=hours)
            self.fueled_until = self.state_time + remaining

    @property
    def time_remaining(self):
        if self.state_time is None:
            return None
        elif self.fueled_until is None:
            return None
        else:
            remaining = self.fueled_until - datetime.utcnow()
            return max(remaining, timedelta(0))

    @property
    def sov_level(self):
        if self.corporation.alliance_id == self.constellation.alliance_id:
            return 'Constellation'
        elif self.corporation.alliance_id == self.solarsystem.alliance_id:
            return 'System'
        else:
            return 'None'

    @property
    def sov_fuel_rate(self):
        if self.sov_level == 'Constellation':
            return Decimal('0.70')
        elif self.sov_level == 'System':
            return Decimal('0.75')
        else:
            return Decimal(1)

    def setup_fuel_supply(self):
        for f in self.tower.fuel.all():
            if f.faction:
                if f.faction != self.solarsystem.faction:
                    continue
                elif self.solarsystem.security < f.minsecuritylevel:
                    continue
            try:
                self.fuel.get(station=self, type=f.type)
            except FuelSupply.DoesNotExist:
                self.fuel.create(
                    type     = f.type,
                    quantity = 0,
                )
                #fuel.solarsystem = self.solarsystem,
                #fuel.constellation = self.moon.constellation
                #fuel.region = self.moon.region
                #fuel.corporation = self.corporation


    @property
    def icon32(self):
        return self.tower.icon32

    def reacted_quantities(self):
        d = {}
        for r in self.reactions.all():
            for item, quantity in r.consumes():
                if d.has_key(item.id):
                    d[item.id]['quantity'] -= quantity
                else:
                    d[item.id] = { 'quantity':-quantity, 'item':item }
            for item, quantity in r.produces():
                if d.has_key(item.id):
                    d[item.id]['quantity'] += quantity
                else:
                    d[item.id] = { 'quantity': quantity, 'item': item }
        return [(x['item'], x['quantity']) for x in d.values()]

    def refresh(self, record, api, corp=None, force=False):
        messages = []

        moon = MapDenormalize.objects.get(id=record.moonID)
        solarsystem = SolarSystem.objects.get(id=record.locationID)
        tower = Item.objects.get(pk=record.typeID)

        if not force and self.cached_until and self.cached_until > datetime.utcnow():
            messages.append("Cached: POS: %s at %s." % (tower, moon))
            return messages

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

        hours_since_update = 0
        if self.state_time and state_time:
            assert isinstance(state_time, datetime)
            assert isinstance(self.state_time, datetime)
            #print "ID:", self.id, "s.st:", self.state_time, "st", state_time
            hours_since_update = state_time - self.state_time
            hours_since_update = hours_since_update.seconds / 60**2

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

        # Now, the fuel.
        for fuel_type in detail.fuel:
            type = Item.objects.get(id=fuel_type.typeID)
            fuel = self.fuel.get(type=type)
            purpose = fuel.purpose

            if (purpose == 'CPU' or purpose == 'Power') and hours_since_update > 0:
                consumed = (fuel.quantity - fuel_type.quantity) / hours_since_update
                max = Decimal(fuel.max_consumption)
                if consumed < 0:
                    continue
                if consumed > max:
                    continue

                if purpose == 'CPU':
                    self.cpu_utilization = consumed / max
                    messages.append("Calculated: CPU Utilization: %0.2f" % self.cpu_utilization)
                else:
                    self.power_utilization = consumed / max
                    messages.append("Calculated: Power Utilization: %0.2f" % self.power_utilization)
                self.save()

            fuel.quantity=fuel_type.quantity
            fuel.save()

        # Once all fuel is loaded, calculate how much runtime that gives us.
        self.update_fueled_until()
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
    #solarsystem = models.ForeignKey('ccp.SolarSystem')
    #constellation = models.ForeignKey('ccp.Constellation')
    #region = models.ForeignKey('ccp.Region')
    #corporation = models.ForeignKey('ccp.Corporation', related_name='pos_fuels')
    quantity = models.IntegerField()

    class Meta:
        ordering = ['type']

    def __unicode__(self):
        return u"%s: %s (%d)" % (self.station, self.type, self.quantity)

    @property
    def fuel_info(self):
        fuel_info = self.station.tower.fuel.get(type=self.type)
        return fuel_info

    @property
    def purpose(self):
        fuel_info = self.station.tower.fuel.get(type=self.type)
        return fuel_info.purpose

    @property
    def max_consumption(self):
        fuel_info = self.fuel_info
        burn_rate = int(fuel_info.quantity)
        if fuel_info.purpose != 'Reinforce':
            burn_rate = math.ceil(burn_rate * self.station.sov_fuel_rate)

        return int(burn_rate)

    @property
    def consumption(self):
        fuel_info = self.fuel_info
        burn_rate = self.max_consumption

        if fuel_info.purpose == 'Power':
            burn_rate = math.ceil(burn_rate * self.station.power_utilization)
        elif fuel_info.purpose == 'CPU':
            burn_rate = math.ceil(burn_rate * self.station.cpu_utilization)

        return int(burn_rate)

    def goal(self, days):
        if self.fuel_info.purpose == 'Reinforce':
            attrib = self.station.tower.attribute_by_name('capacitySecondary')
            max_volume = attrib.value
            need = int(max_volume / self.type.volume)
            return need

        hours = days*24
        need = self.consumption * hours
        return need

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

        if self.type.name == 'Strontium Clathrates':
            if self.station.is_reinforced:
                remaining = self.station.state_time - now
                return max(remaining, timedelta(0))
            else:
                return remaining
        else:
            #remaining += timedelta(hours=1) # Add the remainder of the hour already paid for.
            remaining += self.station.state_time
            remaining -= now
            return max(remaining, timedelta(0))

    @property
    def runs_until(self):
        return datetime.utcnow() + self.time_remaining

class Reaction(models.Model):
    '''
    All of the items that can be mined and/or reacted at a POS.

    This includes moon mining, basic reactions, and advanced reactions.
    '''

    q = Q(group__name__in=['Moon Materials', 'Intermediate Materials',
                           'Composite'])
    q = q & Q(published=True)

    station = models.ForeignKey(PlayerStation)
    type = models.ForeignKey('ccp.Item', limit_choices_to = q,
                             related_name='poses_reacting')

    class Meta:
        ordering = ['type']

    def __unicode__(self):
        return u"%s: %s" % (self.station, self.type)

    @property
    def is_mining(self):
        return self.type.group.name == 'Moon Materials'

    @property
    def is_reaction(self):
        if self.type.group.name == 'Moon Materials':
            return False
        else:
            return True

    def reaction(self):
        return self.type.reacts.all()[0].reaction

    def inputs(self):
        return self.reaction().reactions.filter(input=True)

    def output(self):
        return self.reaction().reactions.filter(input=False)[0]

    @property
    def quantity(self):
        if self.is_mining:
            return 100
        else:
            return self.output().quantity

    def consumes(self):
        '''
        Return a tuple of (item, quantity) for all items consumed by this
        reaction.
        '''
        if self.is_mining:
            return ()
        else:
            return [(i.item, i.quantity) for i in self.inputs()]

    def produces(self):
        '''
        Return a tuple of (item, quantity) for what this reacton outputs.
        '''
        return [(self.type, self.quantity)]
