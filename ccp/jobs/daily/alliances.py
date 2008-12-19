from django_extensions.management.jobs import DailyJob
from eve.util import api_loader

class Job(DailyJob):
    help = "Reload all of the alliances and member corporations."

    def execute(self):
        api_loader.update_alliances()
