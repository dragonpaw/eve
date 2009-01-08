from eve.pos.models import PlayerStation, FuelSupply, Reaction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class FuelSupply_Inline(admin.TabularInline):
    model = FuelSupply

class Reaction_Inline(admin.TabularInline):
    model = Reaction

class FuelSupplyOptions(admin.ModelAdmin):
    list_display = ('station', 'type', 'quantity')
    raw_id_fields = ('station', 'type',)

class ReactionOptions(admin.ModelAdmin):
    list_display = ('station', 'type', )

class PlayerStationOptions(admin.ModelAdmin):
    inlines = [FuelSupply_Inline, Reaction_Inline]
    list_display = ('moon', 'corporation', 'state', 'fueled_until')
    fieldsets = (
        (None, {'fields': ('corporation','moon','tower', 'owner', 'state')}),
        ('Times', {'fields': ('state_time','online_time','cached_until','last_updated'),
                   'classes': ('collapse',)}),
        ('Location', {'fields': ('solarsystem','constellation','region'),
                      'classes': ('collapse',)}),
        ('General Settings', {'fields': ('corporation_use',
                                         'alliance_use',
                                         'deploy_flags',
                                         'usage_flags',
                                         'claim'),
                              'classes': ('collapse',)}),
        ('Combat Settings', {'fields': ('attack_standing_value',
                                        'attack_aggression',
                                        'attack_atwar',
                                        'attack_secstatus_flag',
                                        'attack_secstatus_value'),
                             'classes': ('collapse',)}),
    )
    raw_id_fields = ('moon', 'solarsystem', 'constellation', 'region', 'corporation')

admin.site.register(FuelSupply, FuelSupplyOptions)
admin.site.register(Reaction, ReactionOptions)
admin.site.register(PlayerStation, PlayerStationOptions)
