from eve.trade.models import JournalEntryType, JournalEntry, Transaction, MarketIndex, MarketIndexValue, BlueprintOwned
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class MarketIndexValue_Inline(admin.TabularInline):
    model = MarketIndexValue
    raw_id_fields = ('item',)

class JournalEntryTypeOptions(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_boring',)
    list_display_links = ('name',)

class MarketIndexOptions(admin.ModelAdmin):
    inlines = [MarketIndexValue_Inline]
    list_display = ('id', 'user', 'priority', 'name', 'url', 'note')

class MarketIndexValueOptions(admin.ModelAdmin):
    list_display = ('item', 'index', 'buy', 'sell')
    search_fields = ['item__name']
    raw_id_fields = ('item',)

class BlueprintOwnedOptions(admin.ModelAdmin):
    list_display = ('user', 'blueprint', 'pe', 'me', 'original')
    search_fields = ('user', 'blueprint')
    raw_id_fields = ('blueprint',)

class TransactionOptions(admin.ModelAdmin):
    list_display = ('character', 'time', 'item', 'get_total_formatted',
                    'get_price_formatted', 'sold', 'quantity')
    list_display_links = ('item', )
    list_filter = ('character',)
    raw_id_fields = ('character', 'item', 'station', 'region')

class JournalEntryOptions(admin.ModelAdmin):
    list_display = ('time', 'character', 'client', 'type', 'price',)
    raw_id_fields = ('character',)

admin.site.register(JournalEntryType, JournalEntryTypeOptions)
admin.site.register(MarketIndex, MarketIndexOptions)
admin.site.register(MarketIndexValue, MarketIndexValueOptions)
admin.site.register(BlueprintOwned, BlueprintOwnedOptions)
admin.site.register(Transaction, TransactionOptions)
admin.site.register(JournalEntry, JournalEntryOptions)
