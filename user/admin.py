from eve.user.models import UserProfile, Account, Character, SkillLevel
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class Account_Inline(admin.TabularInline):
    model = Account
    extra = 0

class Character_Inline(admin.StackedInline):
    model = Character
    raw_id_fields = ('corporation',)
    extra = 0

class Skill_Inline(admin.TabularInline):
    model = SkillLevel
    raw_id_fields = ('skill',)
    extra = 0

class AccountOptions(admin.ModelAdmin):
    inlines = [Character_Inline]
    list_display       = ['id', 'user']
    list_display_links = ['id']
    search_fields      = ['user__user__username']
    ordering           = ['user__user__username']

class CharacterOptions(admin.ModelAdmin):
    list_display       = ['name', 'user', 'corporation', 'get_isk_formatted',
                    'get_sp_formatted', 'training_skill', 'training_level']
    inlines            = [Skill_Inline]
    raw_id_fields      = ['corporation']
    search_fields      = ['name', 'user__user__username']

class SkillLevelOptions(admin.ModelAdmin):
    list_display       = ['character', 'skill', 'level']
    list_display_links = ['skill']
    search_fields      = ['character__name']

class UserProfileOptions(admin.ModelAdmin):
    inlines = [Account_Inline]
    list_display = ('user',)

admin.site.register(Account, AccountOptions)
admin.site.register(Character, CharacterOptions)
admin.site.register(SkillLevel, SkillLevelOptions)
admin.site.register(UserProfile, UserProfileOptions)
