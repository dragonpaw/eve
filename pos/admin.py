from eve.pos.models import PlayerStation, PlayerStationFuelSupply, PlayerStationReaction
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class PlayerStationFuelSupply_Inline(admin.TabularInline):
    model = PlayerStationFuelSupply

class PlayerStationReaction_Inline(admin.TabularInline):
    model = PlayerStationReaction

class PlayerStationFuelSupplyOptions(admin.ModelAdmin):
    list_display = ('station', 'type', 'quantity')
    raw_id_fields = ('type', 'solarsystem', 'constellation', 'region', 'corporation')

class PlayerStationReactionOptions(admin.ModelAdmin):
    list_display = ('station', 'type', )

class PlayerStationOptions(admin.ModelAdmin):
    inlines = [PlayerStationFuelSupply_Inline, PlayerStationReaction_Inline]
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

admin.site.register(PlayerStationFuelSupply, PlayerStationFuelSupplyOptions)
admin.site.register(PlayerStationReaction, PlayerStationReactionOptions)
admin.site.register(PlayerStation, PlayerStationOptions)
