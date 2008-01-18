from django.db.models import signals
from django.dispatch import dispatcher
from eve.user.models import UserProfile
from django.contrib.auth.models import User 

def create_profile_for_user(sender, instance, signal, *args, **kwargs):
    try:
        UserProfile.objects.get( user = instance )
    except ( UserProfile.DoesNotExist, AssertionError ):
        profile = UserProfile( user = instance )
        profile.save()

dispatcher.connect(create_profile_for_user, signal=signals.post_save, sender=User)
