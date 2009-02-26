# $Id$
from django_extensions.management.jobs import BaseJob

from eve.ccp.models import Reaction, Item

ALCHEMY = {
  'Unrefined Dysporite Reaction':          {'Dysporite' : 10, 'Mercury': 95 },
  'Unrefined Ferrofluid Reaction':         {'Ferrofluid': 10, 'Hafnium': 95 },
  'Unrefined Fluxed Condensates Reaction': {'Fluxed Condensates': 10, },
  'Unrefined Hyperflurite Reaction':       {'Hyperflurite':10, 'Vanadium': 95},
  'Unrefined Neo Mercurite Reaction':      {'Neo Mercurite': 10, 'Mercury': 95},
  'Unrefined Prometium Reaction':          {'Prometium': 10, 'Cadmium': 95},
}

class Job(BaseJob):
    help = "Change the DB values for POS reactions."
    when = 'once'

    def execute(self):
        # CCP farked up the DB for reactions.
        for r in Reaction.objects.all():
            if r.item.group.name not in (
                                         'Moon Materials',
                                         'Intermediate Materials',
                                         'Composite'
                                        ):
                continue

            starting = r.quantity

            # All original intermediate products are 1 + 1 = 2
            if r.reaction.group.name == 'Simple Reaction':
                if r.reaction.name in ALCHEMY:
                    if not r.input:
                      r.really_delete()
                      print 'Deleted (Alchemy): %s' % r
                      continue
                else:
                    if r.input:
                        r.quantity = 100
                    else:
                        r.quantity = 200
            #elif r.item.group.name == 'Moon Materials':
            #    r.quantity = 100
            elif r.reaction.group.name == 'Complex Reactions':
                if r.input:
                    r.quantity = 100
                else:
                    r.quantity = r.item.attribute_by_name('moonMiningAmount').value

            print "Input: %-30s, Old: %5d, New: %5d" % (r.reaction,
                                                        starting,
                                                        r.quantity
                                                        )
            r.save()

        for a in ALCHEMY.keys():
          reaction = Item.objects.get(name=a)
          for i_name in ALCHEMY[a].keys():
              item = Item.objects.get(name=i_name)
              new = Reaction(reaction=reaction, item=item, quantity=ALCHEMY[a][i_name], input=False)
              print 'Adding (Alchemy): %s' % new
              new.save()
