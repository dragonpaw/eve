from eve.user.models import UserProfile, Account, Character, SkillLevel
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class Account_Inline(admin.TabularInline):
    model = Account

class Character_Inline(admin.TabularInline):
    model = Character

class AccountOptions(admin.ModelAdmin):
    inlines = [Character_Inline]
    list_display = ('user', 'id')
    list_display_links = ('id', )

class CharacterOptions(admin.ModelAdmin):
    list_display = ('name', 'user', 'corporation', 'get_isk_formatted', 
                    'get_sp_formatted', 'training_skill', 'training_level')

class SkillLevelOptions(admin.ModelAdmin):
    search_fields = ('character__name',)
    list_display = ('character', 'skill', 'level')
    list_display_links = ('skill',)

class UserProfileOptions(admin.ModelAdmin):
    inlines = [Account_Inline]
    list_display = ('user',)

admin.site.register(Account, AccountOptions)
admin.site.register(Character, CharacterOptions)
admin.site.register(SkillLevel, SkillLevelOptions)
admin.site.register(UserProfile, UserProfileOptions)

