from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from ccp.models import Agent, AgentType, Alliance, CharacterAncestry, CharacterAttribute, CharacterBloodline, CharacterCareer, CharacterCareerSpeciality, Faction, Race, School, Corporation, CorporationDivision, Attribute, Effect, Graphic, Unit, Category, Group, BlueprintDetail, Material, Item, Name, MarketGroup, InventoryMetaGroup, InventoryMetaType, Reaction, Region, Constellation, SolarSystem, MapDenormalize, RamActivity, Station, PosFuelPurpose, PosFuel, AttributeCategory

class AgentOptions(admin.ModelAdmin):
    search_fields = ('id',)
    list_display = ('id', 'name', 'corporation', 'division', 'station')
    #list_display = ('id', 'name',)
    raw_id_fields = ('corporation', 'station')

class AgentTypeOptions(admin.ModelAdmin):
    search_fields = ('id',)
    list_display = ('id', 'agenttype')

class AllianceOptions(admin.ModelAdmin):
    search_fields = ('name', 'ticker')
    list_display = ('name', 'executor', 'ticker', 'member_count')

class AttributeOptions(admin.ModelAdmin):
    search_fields = ('attributename', 'displayname', 'id')
    list_display = ('id', 'category', 'attributename', 'displayname', 'description', 'unit')

class BlueprintDetailOptions(admin.ModelAdmin):
    search_fields = ('makes__name',)
    list_display = ('id', 'makes',)
    raw_id_fields = ('parent', 'makes')

class CategoryOptions(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'description',)
    raw_id_fields = ('graphic',)

class CharacterAncestryOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'description')
    raw_id_fields = ('graphic',)

class CharacterAttributeOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'description')
    raw_id_fields = ('graphic',)

class CharacterBloodlineOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'description')
    raw_id_fields = ('ship', 'corporation', 'graphic')

class CharacterCareerOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'school', 'description')
    raw_id_fields = ('graphic', 'school')

class CharacterCareerSpecialityOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'career', 'description')
    raw_id_fields = ('graphic',)

class ConstellationOptions(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'faction')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'region', 'faction')
        }),
        ('Location', {
            'classes': ('collapse',),
            'fields': ('radius', 'x', 'y', 'z', 'xmin', 'ymin', 'zmin',
                       'xmax', 'ymax', 'zmax'),
        }),
    )

class Constellation_Inline(admin.TabularInline):
    model = Constellation

class CorporationDivisionOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'description',)

class CorporationOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name', 'is_player_corp')

class EffectOptions(admin.ModelAdmin):
    search_fields = ('name', 'displayname', 'id')
    list_display = ('id', 'name', 'displayname', 'description',)

class FactionOptions(admin.ModelAdmin):
    search_fields = ('name', 'id')
    list_display = ('name', 'description')

class GraphicOptions(admin.ModelAdmin):
    search_fields = ('id', 'icon', 'description')
    list_display = ('id', 'icon', 'url3d', 'urlweb', 'description')

class GroupOptions(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'category', 'graphic', 'description',)
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'category', 'description', 'graphic'),
        }),
        ('Flags', {
            'fields': ('usebaseprice', 'allowmanufacture', 'allowrecycler',
                       'anchored', 'anchorable'),
        })
    )

class InventoryMetaGroupOptions(admin.ModelAdmin):
    search_fields = ('name', 'id')
    list_display = ('id', 'name', 'description')
    list_select_related = True
    raw_id_fields = ('graphic',)

class InventoryMetaTypeOptions(admin.ModelAdmin):
    search_fields = ('id', 'metagroup__name', 'parent__name')
    list_display = ('item', 'metagroup', 'parent')
    list_select_related = True
    raw_id_fields = ('item', 'parent')

class ItemOptions(admin.ModelAdmin):
    search_fields = ('name', 'id')
    list_display = ('name', 'id', 'group', 'category', 'graphic')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'group', 'marketgroup', 'real_description',
                       'graphic', 'race'),
        }),
        ('Physics', {
            'fields': ('mass', 'volume', 'radius', 'portionsize')
        }),
        ('Misc', {
            'fields': ('published', 'baseprice', 'chanceofduplicating'),
        })
    )
    list_filter = ('group',)
    raw_id_fields = ('graphic',)

class MapDenormalizeOptions(admin.ModelAdmin):
    raw_id_fields = ('orbits',)

class MarketGroupOptions(admin.ModelAdmin):
    search_fields = ('name',)
    #radio_fields = ('hastypes',)
    list_display = ('name', 'slug', 'description', 'graphic')

class MaterialOptions(admin.ModelAdmin):
    search_fields = ('item',)
    list_display = ('item', 'activity', 'material', 'quantity',)
    raw_id_fields = ('item', 'material')

class NameOptions(admin.ModelAdmin):
    search_fields = ('name', 'id')
    # Don't ask why, but adding type or group makes the admin list show
    # no rows at all.
    list_display = ('name', 'category', 'group')
    list_filter = ('group',)
    raw_id_fields = ('type',)

class PosFuelOptions(admin.ModelAdmin):
    raw_id_fields = ('type',)

class RaceOptions(admin.ModelAdmin):
    search_fields = ('name', 'id')
    list_display = ('name', 'description')
    raw_id_fields = ('graphic',)

class RegionOptions(admin.ModelAdmin):
    inlines = [Constellation_Inline]
    search_fields = ('name',)
    list_display = ('name', 'faction')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'faction')
        }),
        ('Location', {
            'fields': ('radius', 'x', 'y', 'z', 'xmin', 'ymin', 'zmin',
                       'xmax', 'ymax', 'zmax'),
        }),
    )

class SchoolOptions(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name')
    raw_id_fields = ('graphic', 'corporation', 'agent')

class SolarSystemOptions(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'region', 'constellation', 'security',)
    raw_id_fields = ('constellation',)

class StationOptions(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'region', 'constellation', 'corporation', 'type')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'corporation', 'type')
        }),
        ('Corp', {
         'fields': ('dockingcostpervolume', 'maxshipvolumedockable',
                    'officerentalcost'),
         }),
        ('Reprocessing', {
         'fields': ('reprocessingefficiency', 'reprocessingstationstake',
                    'reprocessinghangarflag'),
         }),
        ('Location', {
            'fields': ('region', 'constellation', 'solarsystem', 'x', 'y', 'z',),
        }),
    )
    list_filter = ('region',)
    raw_id_fields = ('solarsystem', 'constellation', 'type', 'region', 'corporation')

class UnitOptions(admin.ModelAdmin):
    search_fields = ('id',)
    list_display = ('id', 'name', 'description')

admin.site.register(Agent, AgentOptions)
admin.site.register(AgentType, AgentTypeOptions)
admin.site.register(Alliance, AllianceOptions)
admin.site.register(Attribute, AttributeOptions)
admin.site.register(AttributeCategory)
admin.site.register(BlueprintDetail, BlueprintDetailOptions)
admin.site.register(Category, CategoryOptions)
admin.site.register(CharacterAncestry, CharacterAncestryOptions)
admin.site.register(CharacterAttribute, CharacterAttributeOptions)
admin.site.register(CharacterBloodline, CharacterBloodlineOptions)
admin.site.register(CharacterCareer, CharacterCareerOptions)
admin.site.register(CharacterCareerSpeciality, CharacterCareerSpecialityOptions)
admin.site.register(Constellation, ConstellationOptions)
admin.site.register(Corporation, CorporationOptions)
admin.site.register(CorporationDivision, CorporationDivisionOptions)
admin.site.register(Effect, EffectOptions)
admin.site.register(Faction, FactionOptions)
admin.site.register(Graphic, GraphicOptions)
admin.site.register(Group, GroupOptions)
admin.site.register(InventoryMetaGroup, InventoryMetaGroupOptions)
admin.site.register(InventoryMetaType, InventoryMetaTypeOptions)
admin.site.register(Item, ItemOptions)
admin.site.register(MapDenormalize, MapDenormalizeOptions)
admin.site.register(MarketGroup, MarketGroupOptions)
admin.site.register(Material, MaterialOptions)
admin.site.register(Name, NameOptions)
admin.site.register(PosFuel, PosFuelOptions)
admin.site.register(PosFuelPurpose)
admin.site.register(Race, RaceOptions)
admin.site.register(RamActivity)
admin.site.register(Reaction)
admin.site.register(Region, RegionOptions)
admin.site.register(School, SchoolOptions)
admin.site.register(SolarSystem, SolarSystemOptions)
admin.site.register(Station, StationOptions)
admin.site.register(Unit, UnitOptions)
