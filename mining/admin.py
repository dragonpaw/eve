from eve.mining.models import MiningOp, MinerOnOp, MiningOpMineral
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class MinerOnOp_Inline(admin.TabularInline):
    model = MinerOnOp

class MiningOpMineral_Inline(admin.TabularInline):
    model = MiningOpMineral

class MiningOpOptions(admin.ModelAdmin):
    inlines = [MinerOnOp_Inline, MiningOpMineral_Inline]
    list_display = ['id', 'description', 'hours']

class MinerOnOpOptions(admin.ModelAdmin):
    list_display = ['id', 'op', 'name', 'multiplier', 'hours', 'percent']

class MiningOpMineralOptions(admin.ModelAdmin):
    list_display = ['id', 'op', 'type', 'quantity']

admin.site.register(MiningOp, MiningOpOptions)
admin.site.register(MinerOnOp, MinerOnOpOptions)
admin.site.register(MiningOpMineral, MiningOpMineralOptions)

