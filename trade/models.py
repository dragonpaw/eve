#from django.contrib.auth.models import User 
from django.db import models
from eve.ccp.models import Item, Region, Station
from eve.util.formatting import comma
from eve.user.models import Character, UserProfile
from datetime import date
from decimal import Decimal

class JournalEntryType(models.Model):
    name = models.CharField(max_length=100)
    is_boring = models.BooleanField(default=False)
    
    class Admin:
        list_display = ('name', 'is_boring',)
    
    class Meta:
        ordering = ('name',)
        
    def __str__(self):
        return self.name

class JournalEntry(models.Model):
    transaction_id = models.IntegerField('ID')
    character = models.ForeignKey(Character, related_name='journal', raw_id_admin=True)
    type = models.ForeignKey(JournalEntryType)
    client = models.CharField(max_length=100)
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    reason = models.CharField(max_length=200)
    
    class Admin:
        list_display = ('time', 'character', 'client', 'type', 'price',)
        
    class Meta:
        ordering = ('-time',)
        
    def __str__(self):
        if self.price < 0:
            return "%s: %s -> %s" % (self.type, self.price, self.client)
        else:
            return "%s: %s <= %s" % (self.type, self.price, self.client)
        
    def get_absolute_url(self):
        return "/trade/journal/%d/" % self.transaction_id

    @property
    def name(self):
        return "J: %s" % self.transaction_id

    @property
    def is_transaction(self):
        return False
    
    @property
    def sold(self):
        return self.price > 0
    
    @property
    def value(self):
        if self.sold:
            return self.price
        else:
            return (self.price * Decimal(-1))

    @property
    def icon32(self):
        return '/static/ccp-icons/white/32_32/icon06_03.png'

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
        
    def get_absolute_url(self):
        return "/trade/transaction/%d/" % self.transaction_id

    @property
    def is_transaction(self):
        return True
    
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
        
    def get_name(self):
        return "T: %d" % self.transaction_id
    name = property(get_name)
    
    @property
    def icon32(self):
        return self.item.icon32
    
class MarketIndex(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200, blank=True)
    note = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(UserProfile, blank=True, null=True, related_name='indexes')
    priority = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Market Indexes"
        ordering = ['name']
    
    class Admin:
        list_display = ('id', 'user', 'priority', 'name', 'url', 'note')
    
    def __str__(self):
        if self.user:
            return "%s: %s" % (self.name, self.user)
        else:
            return self.name
        
    def get_absolute_url(self):
        return "/trade/index/%s/" % (self.name)
        
    def set_value(self, item, buy=0, sell=0, buy_qty=0, sell_qty=0):
        assert(isinstance(item, Item))
        #print "self: %s, item: %s, b: %s/%s s: %s/%s" % (self, item, buy, buy_qty, sell, sell_qty)
        if sell:
            sell = Decimal(str(sell))
        else:
            sell = 0
            
        if buy:
            buy = Decimal(str(buy))
        else:
            buy = 0
            
        if buy==0 and sell==0:
            #print "Deleting index price."
            return self.items.filter(item=item).delete()
        #print "Updating index."
        try:
            index = self.items.get(item=item)
        except MarketIndexValue.DoesNotExist:
            index = MarketIndexValue(index=self, item=item)
        index.buy = buy
        index.sell = sell
        index.date = date.today()
        index.buy_qty = buy_qty
        index.sell_qty = sell_qty
        index.save()
        return index
        
class MarketIndexValue(models.Model):
    item = models.ForeignKey(Item, raw_id_admin=True, related_name='index_values', core=True)
    index = models.ForeignKey(MarketIndex, related_name='items', edit_inline = models.TABULAR)
    date = models.DateField()
    buy = models.FloatField(core=True)
    sell = models.FloatField(core=True)
    buy_qty = models.IntegerField(blank=True, default=0)
    sell_qty = models.IntegerField(blank=True, default=0)
    
    class Meta:
        ordering = ['item']
    
    class Admin:
        list_display = ('item', 'index', 'buy', 'sell')
        search_fields = ['item__name']
    
    def __str__(self):
        return "%s: %f/%f" % (self.item, self.buy, self.sell)
        
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
            
