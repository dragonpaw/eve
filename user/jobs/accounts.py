from eve.lib.log import BaseJob
import traceback

from eve.lib import eveapi
from eve.user.models import UserProfile

class Job(BaseJob):
    help = "Reload all of the alliances and member corporations."
    when = '5min'

    def execute(self, user=None, force=False):
        messages = []
        api = eveapi.get_api()
        log = self.logger()

        if user:
            log.info("Only loading characters for: %s", user)
            users = UserProfile.objects.filter(user__username=user)
        else:
            # All the non-stale users.
            q = UserProfile.objects.order_by('user__username')
            users = [u for u in q if not u.is_stale]

        if force:
            log.info("Forcing reload, cache times will be ignored.")

        for u in users:
            log.info("User: %s", u)
            m = []
            for a in u.accounts.all():
                log.info("Account: %s", a.id)
                try:
                    messages = a.refresh(force=force)
                except Exception, e:
                    if 'EVE backend database temporarily disabled' in str(e):
                        log.warn('EVE API taken offline by CCP. No refresh today.')
                        return False
                    else:
                        text = traceback.format_exc()
                        m.append(text)
                        log.error(text)
