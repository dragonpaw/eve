from django.db import models
from django.db.models.query import Q, QNot
from datetime import datetime, timedelta
from decimal import Decimal
import math

from eve.ccp.models import (MapDenormalize, Item, SolarSystem, Region, Constellation, Corporation,
                            StationResource)

class FuelDepot(models.Model):
    location = models.ForeignKey(SolarSystem)
    note = models.TextField()
    
    def __str__(self):
        if (self.note == ""):
            return self.locaiton
        else:
            return "%s (%s)" % (self.location, self.note)
        
    class Admin:
        list_display = ('location', 'note')

class FuelSupply(models.Model):
    depot = models.ForeignKey(FuelDepot)
    type = models.ForeignKey(Item, raw_id_admin=True)
    #                              limit_choices_to = {'is_pos_fuel': True})
    quantity = models.IntegerField()
    
    def __str__(self):
        return "%s: %s" % (self.depot.location, self.type)

    class Admin:
        list_display = ('depot', 'type', 'quantity')
        
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
    
    moon = models.ForeignKey(MapDenormalize, raw_id_admin=True)
    solarsystem = models.ForeignKey(SolarSystem)
    constellation = models.ForeignKey(Constellation)
    region = models.ForeignKey(Region)
    tower = models.ForeignKey(Item, limit_choices_to = q)
    note = models.CharField(max_length=500, blank=True)
    depot = models.ForeignKey(FuelDepot, blank=True, null=True)
    state = models.IntegerField(choices=POS_STATES)
    state_time = models.DateTimeField(blank=True)
    online_time = models.DateTimeField(blank=True)
    cached_until = models.DateTimeField(blank=True)
    last_updated = models.DateTimeField(blank=True)
    corporation = models.ForeignKey(Corporation, related_name='pos')
    #corp = models.ForeignKey(PlayerCorp)
    
    corporation_use = models.BooleanField()
    alliance_use = models.BooleanField()
    deploy_flags = models.IntegerField(blank=True)
    usage_flags = models.IntegerField(blank=True)
    claim = models.BooleanField()
    
    attack_standing_flag = models.BooleanField()
    attack_standing_value = models.FloatField()
    attack_aggression = models.BooleanField()
    attack_atwar = models.BooleanField()
    attack_secstatus_flag = models.BooleanField()
    attack_secstatus_value = models.FloatField()
    
    cpu_utilization = models.DecimalField(default=1, max_digits=6, decimal_places=4)
    power_utilization = models.DecimalField(default=1, max_digits=6, decimal_places=4)
    
    class Meta:
        ordering = ['moon']
    
    class Admin:
        list_display = ('moon', 'corporation', 'depot', 'state')

    def __str__(self):
        return "%s (%s)" % (self.moon, self.corporation)
    
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
        return "/pos/%d/detail/" % self.id

    @property
    def cache_remaining(self):
        return max(self.cached_until - datetime.utcnow(), timedelta(0))

    @property
    def hours_of_fuel(self):
        return min([f.hours_of_fuel for f in self.fuel.exclude(type__name='Strontium Clathrates')])

    @property
    def fuel_needed(self):
        hours = self.hours_of_fuel
        fuels = [f.type for f in self.fuel.exclude(type__name='Strontium Clathrates') if f.hours_of_fuel == hours]
        return fuels

    @property
    def time_remaining(self):
        remaining = timedelta(hours=self.hours_of_fuel) 
        #remaining += timedelta(hours=1) # Add the remainder of the hour already paid for.
        remaining += self.state_time
        remaining -= datetime.utcnow()
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
        if self.corporation.alliance_id == self.constellation.alliance_id:
            return Decimal('0.70')
        elif self.corporation.alliance_id == self.solarsystem.alliance_id:
            return Decimal('0.75')
        else:
            return Decimal(1)

    def setup_fuel_supply(self):
        for fuel in self.tower.fuel.all():
            if fuel.faction:
                if fuel.faction != self.solarsystem.faction:
                    continue
                elif self.solarsystem.security < fuel.minsecuritylevel:
                    continue
            PlayerStationFuelSupply.objects.get_or_create(station=self,
                                                          type=fuel.type,
                                                          defaults={'quantity':0,
                                                                    'solarsystem':self.solarsystem,
                                                                    'constellation':self.moon.constellation,        
                                                                    'region':self.moon.region,
                                                                    'corporation':self.corporation,})
                
        
    #@property
    #def fuel(self):
    #    return StationResource.objects.filter(tower=self.tower)

class PlayerStationModule(models.Model):
    q = Q(group__category__name='Structure', published=True) & QNot(Q(group__name='Control Tower'))
    
    item = models.ForeignKey(Item, limit_choices_to = q)
    station = models.ForeignKey(PlayerStation)
    online = models.BooleanField(default=True)
    
    def __str__(self):
        return "%s" % (self.item)
    
    class Admin:
        list_display = ('station', 'item')
        list_display_links = ['item']
        
class PlayerStationFuelSupply(models.Model):
    station = models.ForeignKey(PlayerStation, related_name='fuel')
    type = models.ForeignKey(Item, raw_id_admin=True, related_name='active_stations_using')
    #                              limit_choices_to = {'is_pos_fuel': True})
    solarsystem = models.ForeignKey(SolarSystem)
    constellation = models.ForeignKey(Constellation)
    region = models.ForeignKey(Region)
    corporation = models.ForeignKey(Corporation, related_name='pos_fuels')

    quantity = models.IntegerField()
    
    def __str__(self):
        return "%s: %s (%d)" % (self.station, self.type, self.quantity)

    class Admin:
        list_display = ('station', 'type', 'quantity')
        
    class Meta:
        ordering = ['type']
    
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

    def need(self, days=14):
        if self.fuel_info.purpose == 'Reinforce':
            return None
        
        hours = days*24
        need = (self.consumption * hours) - self.quantity
        return max(need, 0)

    @property
    def hours_of_fuel(self):
        return int(self.quantity / self.consumption)
    
    @property
    def time_remaining(self):
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