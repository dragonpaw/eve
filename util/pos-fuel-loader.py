import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from eve.ccp.models import Item

fuels = (
         'Helium Isotopes', 'Oxygen Isotopes', 'Nitrogen Isotopes', 'Hydrogen Isotopes', 
         'Robotics', 'Coolant', 'Mechanical Parts',
         'Oxygen',
         'Enriched Uranium',
         'Strontium Clathrates',
         'Liquid Ozone', 'Heavy Water',
         'Amarr Empire Starbase Charter', 'Caldari State Starbase Charter',
         'Gallente Federation Starbase Charter', 'Minmatar Republic Starbase Charter',
         'Khanid Kingdom Starbase Charter', 'Ammatar Mandate Starbase Charter',
         )

for name in fuels:
    item = Item.objects.get(name=name)
    print "Altering: %s (%s)" % (name, item.id)
    item.is_pos_fuel = True
    item.save()

