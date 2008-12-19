from django_extensions.management.jobs import BaseJob

from eve.trade.models import JournalEntryType
from eve.lib.cachehandler import MyCacheHandler
from eve.lib import eveapi

boring = (
    'Market Transaction',
    'Transaction Tax',
    'Market Escrow',
    'Broker fee',
    'Contract Brokers fee'
)

class Job(BaseJob):
    help = "Create the Entry objects from API."
    when = 'once'

    def execute(self):
        api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True, throw=False)).context(version=2)
        JournalEntryType.objects.all().delete()
        for t in api.eve.RefTypes().refTypes:
            id = t.refTypeID
            name = t.refTypeName
            entry = JournalEntryType(id=id, name=name)
            if name in boring:
                entry.is_boring = True
            entry.save()
            print "%-3s %-40s Boring: %s" % (entry.id, entry.name, entry.is_boring)
