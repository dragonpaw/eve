from django_extensions.management.jobs import DailyJob
from eve.util import api_loader

class Job(DailyJob):
    help = "Reload all of the soverignity data."

    def execute(self):
        api_loader.update_map()
