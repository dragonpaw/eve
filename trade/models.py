#from django.contrib.auth.models import User 
from django.db import models
from eve.ccp.models import *
from eve.util.formatting import comma
from eve.user.models import Character, UserProfile

# Create your models here.
class Transaction(models.Model):
    transaction_id = models.IntegerField('ID')
    character = models.ForeignKey(Character, related_name='transactions',
                                  raw_id_admin=True)
    item = models.ForeignKey(Item, raw_id_admin=True)
    sold = models.BooleanField()
    price = models.FloatField()
    quantity = models.IntegerField()
    station = models.ForeignKey(Station, raw_id_admin=True)
    region = models.ForeignKey(Region, raw_id_admin=True)
    time = models.DateTimeField()
    client = models.CharField(max_length=100)
    
    class Admin:
        list_display = ('character', 'time', 'item', 'get_total_formatted',
                        'get_price_formatted', 'sold', 'quantity')
        list_display_links = ('item', )
        list_filter = ('character',)
        
    class Meta:
        ordering = ('-time',)
        
    def __str__(self):
        return "T: %i" % self.transaction_id
        
    def get_price_formatted(self):
        return comma(self.price) + ' ISK'
    get_price_formatted.short_description="ISK Each"
    price_formatted = property(get_price_formatted)
    
    def get_value(self):
        return self.price * self.quantity
    value = property(get_value) 
    
    def get_total(self):
        total = self.price * self.quantity
        if self.sold:
            return total
        else:
            return -1 * total
    get_total.short_description =  'Total'
    total = property(get_total)

    def get_total_formatted(self):
        return comma( self.total ) + ' ISK'
    get_total_formatted.short_description = 'Total'
    total_formatted = property(get_total_formatted)
        
    def get_absolute_url(self):
        return "/trade/transaction/%d/" % self.transaction_id
    
    def get_name(self):
        return "T: %d" % self.transaction_id
    name = property(get_name)
    
class MarketIndex(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Market Indexes"
        ordering = ['name']
    
    class Admin:
        list_display = ('id', 'name', 'url')
    
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/trade/index/%d/" % (self.id)
        
class MarketIndexValue(models.Model):
    item = models.ForeignKey(Item, raw_id_admin=True, related_name='index_values')
    index = models.ForeignKey(MarketIndex, related_name='items')
    date = models.DateField()
    value = models.FloatField()
    class Meta:
        ordering = ['item']
    
    class Admin:
        list_display = ('item', 'index', 'value')
    
    def __str__(self):
        return "%s: %f" % (self.item, self.value)
        
class BlueprintOwned(models.Model):
    user = models.ForeignKey(UserProfile, related_name='blueprints')
    blueprint = models.ForeignKey(Item,
                                  raw_id_admin=True,
                                  limit_choices_to = {'group__category__name__exact': 'Blueprint',
                                                      'published':True})
    pe = models.IntegerField('Production Efficiency', default=0)
    me = models.IntegerField('Material Efficiency', default=0)
    original = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('blueprint',)
        verbose_name_plural = "Blueprints Owned"
        
    class Admin:
        list_display = ('user', 'blueprint', 'pe', 'me', 'original')
        search_fields = ('user', 'blueprint')
        
    def __str__(self):
        return self.blueprint.name
    
    def waste(self):
        base = Decimal(self.blueprint.blueprint_details.wastefactor)
        # Base is stored as full percentage.
        base = base / 100
        return Decimal(str(base))/(1+self.me)
        
    def waste_display(self):
        return "%0.2f %%" % (self.waste()*100)
        
    def mineral(self, base, pe_skill):
        base = Decimal(base)
        waste = 1 + self.waste()
        pe_mod = 1 + ( Decimal("0.05") * (5 - pe_skill) )
        min = base * waste * pe_mod
        return int(round(min))
        
    def manafuc_time(self, base, industry):
        base = Decimal(base) 
        blueprint_mod = 1 - ( self.pe / base ) * ( self.pe / ( 1 + self.pe ) )
        industry_mod = 1 - (Decimal("0.04")*industry)
        time =  base * industry_mod * blueprint_mod
        return time
        
    def minerals(self, character):
        minerals = self.blueprint.get_materials()
        pe_skill = character.skills.get(name='Production Efficiency').level
        for m in minerals:
            # mineral, qty = m
            qty = self.mineral(m[1], pe_skill)
            m[1] = qty
        return minerals
            
