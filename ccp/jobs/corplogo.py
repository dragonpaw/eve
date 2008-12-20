from django_extensions.management.jobs import BaseJob

from eve.ccp.models import Corporation

class Job(BaseJob):
    help = "Create icons for all corporations."
    when = 'once'

    def execute(self):
        for c in Corporation.objects.all():
            if not c.is_player_corp:
                continue
            
            message = c.updatelogo()
            if message != 'No logo generation required.':
                print message
