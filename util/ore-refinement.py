import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from eve.ccp.models import Material, Item, RamActivity

Refine = RamActivity.objects.get(name='Refining')
# Purge so that we can reload.
Material.objects.filter(activity=Refine).delete()

Tritanium = Item.objects.get(name='Tritanium')
Pyerite = Item.objects.get(name='Pyerite')
Mexallon = Item.objects.get(name='Mexallon')
Isogen = Item.objects.get(name='Isogen')
Nocxium = Item.objects.get(name='Nocxium')
Zydrine = Item.objects.get(name='Zydrine')
Megacyte = Item.objects.get(name='Megacyte')
Morphite = Item.objects.get(name='Morphite')

# Tritanium
Material(item=Item.objects.get(name='Veldspar'), material=Tritanium, quantity=1000, activity=Refine).save()
Material(item=Item.objects.get(name='Concentrated Veldspar'), material=Tritanium, quantity=1050, activity=Refine).save()
Material(item=Item.objects.get(name='Dense Veldspar'), material=Tritanium, quantity=1100, activity=Refine).save()

# Tritanium, Pyerite
Material(item=Item.objects.get(name='Scordite'), material=Tritanium, quantity=833, activity=Refine).save()
Material(item=Item.objects.get(name='Scordite'), material=Pyerite, quantity=416, activity=Refine).save()
Material(item=Item.objects.get(name='Condensed Scordite'), material=Tritanium, quantity=875, activity=Refine).save()
Material(item=Item.objects.get(name='Condensed Scordite'), material=Pyerite, quantity=437, activity=Refine).save()
Material(item=Item.objects.get(name='Massive Scordite'), material=Tritanium, quantity=916, activity=Refine).save()
Material(item=Item.objects.get(name='Massive Scordite'), material=Pyerite, quantity=458, activity=Refine).save()

# Tritanium, Pyerite, Mexallon, Nocxium
Material(item=Item.objects.get(name='Pyroxeres'), material=Tritanium, quantity=844, activity=Refine).save()
Material(item=Item.objects.get(name='Pyroxeres'), material=Pyerite, quantity=59, activity=Refine).save()
Material(item=Item.objects.get(name='Pyroxeres'), material=Mexallon, quantity=120, activity=Refine).save()
Material(item=Item.objects.get(name='Pyroxeres'), material=Nocxium, quantity=11, activity=Refine).save()
Material(item=Item.objects.get(name='Solid Pyroxeres'), material=Tritanium, quantity=886, activity=Refine).save()
Material(item=Item.objects.get(name='Solid Pyroxeres'), material=Pyerite, quantity=62, activity=Refine).save()
Material(item=Item.objects.get(name='Solid Pyroxeres'), material=Mexallon, quantity=126, activity=Refine).save()
Material(item=Item.objects.get(name='Solid Pyroxeres'), material=Nocxium, quantity=12, activity=Refine).save()
Material(item=Item.objects.get(name='Viscous Pyroxeres'), material=Tritanium, quantity=928, activity=Refine).save()
Material(item=Item.objects.get(name='Viscous Pyroxeres'), material=Pyerite, quantity=65, activity=Refine).save()
Material(item=Item.objects.get(name='Viscous Pyroxeres'), material=Mexallon, quantity=132, activity=Refine).save()
Material(item=Item.objects.get(name='Viscous Pyroxeres'), material=Nocxium, quantity=12, activity=Refine).save()

# Tritanium, Pyerite, Mexallon
Material(item=Item.objects.get(name='Plagioclase'), material=Tritanium, quantity=256, activity=Refine).save()
Material(item=Item.objects.get(name='Plagioclase'), material=Pyerite, quantity=512, activity=Refine).save()
Material(item=Item.objects.get(name='Plagioclase'), material=Mexallon, quantity=256, activity=Refine).save()
Material(item=Item.objects.get(name='Azure Plagioclase'), material=Tritanium, quantity=269, activity=Refine).save()
Material(item=Item.objects.get(name='Azure Plagioclase'), material=Pyerite, quantity=538, activity=Refine).save()
Material(item=Item.objects.get(name='Azure Plagioclase'), material=Mexallon, quantity=269, activity=Refine).save()
Material(item=Item.objects.get(name='Rich Plagioclase'), material=Tritanium, quantity=282, activity=Refine).save()
Material(item=Item.objects.get(name='Rich Plagioclase'), material=Pyerite, quantity=563, activity=Refine).save()
Material(item=Item.objects.get(name='Rich Plagioclase'), material=Mexallon, quantity=282, activity=Refine).save()

# Tritanium, Pyerite, Isogen
Material(item=Item.objects.get(name='Omber'), material=Tritanium, quantity=307, activity=Refine).save()
Material(item=Item.objects.get(name='Omber'), material=Pyerite, quantity=123, activity=Refine).save()
Material(item=Item.objects.get(name='Omber'), material=Isogen, quantity=307, activity=Refine).save()
Material(item=Item.objects.get(name='Silvery Omber'), material=Tritanium, quantity=322, activity=Refine).save()
Material(item=Item.objects.get(name='Silvery Omber'), material=Pyerite, quantity=129, activity=Refine).save()
Material(item=Item.objects.get(name='Silvery Omber'), material=Isogen, quantity=322, activity=Refine).save()
Material(item=Item.objects.get(name='Golden Omber'), material=Tritanium, quantity=338, activity=Refine).save()
Material(item=Item.objects.get(name='Golden Omber'), material=Pyerite, quantity=135, activity=Refine).save()
Material(item=Item.objects.get(name='Golden Omber'), material=Isogen, quantity=338, activity=Refine).save()

# Tritanium, Mexallon, Isogen
Material(item=Item.objects.get(name='Kernite'), material=Tritanium, quantity=386, activity=Refine).save()
Material(item=Item.objects.get(name='Kernite'), material=Mexallon, quantity=773, activity=Refine).save()
Material(item=Item.objects.get(name='Kernite'), material=Isogen, quantity=386, activity=Refine).save()
Material(item=Item.objects.get(name='Luminous Kernite'), material=Tritanium, quantity=405, activity=Refine).save()
Material(item=Item.objects.get(name='Luminous Kernite'), material=Mexallon, quantity=812, activity=Refine).save()
Material(item=Item.objects.get(name='Luminous Kernite'), material=Isogen, quantity=405, activity=Refine).save()
Material(item=Item.objects.get(name='Fiery Kernite'), material=Tritanium, quantity=425, activity=Refine).save()
Material(item=Item.objects.get(name='Fiery Kernite'), material=Mexallon, quantity=850, activity=Refine).save()
Material(item=Item.objects.get(name='Fiery Kernite'), material=Isogen, quantity=425, activity=Refine).save()

# Tritanium, Pyerite, Mexallon, Nocxium, Zydrine
Material(item=Item.objects.get(name='Jaspet'), material=Tritanium, quantity=259, activity=Refine).save()
Material(item=Item.objects.get(name='Jaspet'), material=Pyerite, quantity=259, activity=Refine).save()
Material(item=Item.objects.get(name='Jaspet'), material=Mexallon, quantity=518, activity=Refine).save()
Material(item=Item.objects.get(name='Jaspet'), material=Nocxium, quantity=259, activity=Refine).save()
Material(item=Item.objects.get(name='Jaspet'), material=Zydrine, quantity=8, activity=Refine).save()
Material(item=Item.objects.get(name='Pure Jaspet'), material=Tritanium, quantity=272, activity=Refine).save()
Material(item=Item.objects.get(name='Pure Jaspet'), material=Pyerite, quantity=272, activity=Refine).save()
Material(item=Item.objects.get(name='Pure Jaspet'), material=Mexallon, quantity=544, activity=Refine).save()
Material(item=Item.objects.get(name='Pure Jaspet'), material=Nocxium, quantity=272, activity=Refine).save()
Material(item=Item.objects.get(name='Pure Jaspet'), material=Zydrine, quantity=8, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine Jaspet'), material=Tritanium, quantity=285, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine Jaspet'), material=Pyerite, quantity=285, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine Jaspet'), material=Mexallon, quantity=570, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine Jaspet'), material=Nocxium, quantity=285, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine Jaspet'), material=Zydrine, quantity=9, activity=Refine).save()

# Tritanium, Isogen, Nocxium, Zydrine
Material(item=Item.objects.get(name='Hemorphite'), material=Tritanium, quantity=212, activity=Refine).save()
Material(item=Item.objects.get(name='Hemorphite'), material=Isogen, quantity=212, activity=Refine).save()
Material(item=Item.objects.get(name='Hemorphite'), material=Nocxium, quantity=424, activity=Refine).save()
Material(item=Item.objects.get(name='Hemorphite'), material=Zydrine, quantity=28, activity=Refine).save()
Material(item=Item.objects.get(name='Vivid Hemorphite'), material=Tritanium, quantity=223, activity=Refine).save()
Material(item=Item.objects.get(name='Vivid Hemorphite'), material=Isogen, quantity=223, activity=Refine).save()
Material(item=Item.objects.get(name='Vivid Hemorphite'), material=Nocxium, quantity=445, activity=Refine).save()
Material(item=Item.objects.get(name='Vivid Hemorphite'), material=Zydrine, quantity=29, activity=Refine).save()
Material(item=Item.objects.get(name='Radiant Hemorphite'), material=Tritanium, quantity=233, activity=Refine).save()
Material(item=Item.objects.get(name='Radiant Hemorphite'), material=Isogen, quantity=233, activity=Refine).save()
Material(item=Item.objects.get(name='Radiant Hemorphite'), material=Nocxium, quantity=466, activity=Refine).save()
Material(item=Item.objects.get(name='Radiant Hemorphite'), material=Zydrine, quantity=31, activity=Refine).save()

# Isogen, Nocxium, Zydrine
Material(item=Item.objects.get(name='Hedbergite'), material=Isogen, quantity=708, activity=Refine).save()
Material(item=Item.objects.get(name='Hedbergite'), material=Nocxium, quantity=354, activity=Refine).save()
Material(item=Item.objects.get(name='Hedbergite'), material=Zydrine, quantity=32, activity=Refine).save()
Material(item=Item.objects.get(name='Vitric Hedbergite'), material=Isogen, quantity=743, activity=Refine).save()
Material(item=Item.objects.get(name='Vitric Hedbergite'), material=Nocxium, quantity=372, activity=Refine).save()
Material(item=Item.objects.get(name='Vitric Hedbergite'), material=Zydrine, quantity=34, activity=Refine).save()
Material(item=Item.objects.get(name='Glazed Hedbergite'), material=Isogen, quantity=779, activity=Refine).save()
Material(item=Item.objects.get(name='Glazed Hedbergite'), material=Nocxium, quantity=389, activity=Refine).save()
Material(item=Item.objects.get(name='Glazed Hedbergite'), material=Zydrine, quantity=35, activity=Refine).save()

# Tritanium, Pyerite, Megacyte
Material(item=Item.objects.get(name='Spodumain'), material=Tritanium, quantity=700, activity=Refine).save()
Material(item=Item.objects.get(name='Spodumain'), material=Pyerite, quantity=140, activity=Refine).save()
Material(item=Item.objects.get(name='Spodumain'), material=Megacyte, quantity=140, activity=Refine).save()
Material(item=Item.objects.get(name='Bright Spodumain'), material=Tritanium, quantity=735, activity=Refine).save()
Material(item=Item.objects.get(name='Bright Spodumain'), material=Pyerite, quantity=147, activity=Refine).save()
Material(item=Item.objects.get(name='Bright Spodumain'), material=Megacyte, quantity=147, activity=Refine).save()
Material(item=Item.objects.get(name='Gleaming Spodumain'), material=Tritanium, quantity=770, activity=Refine).save()
Material(item=Item.objects.get(name='Gleaming Spodumain'), material=Pyerite, quantity=154, activity=Refine).save()
Material(item=Item.objects.get(name='Gleaming Spodumain'), material=Megacyte, quantity=154, activity=Refine).save()

# Tritanium, Mexallon, Isogen, Zydrine
Material(item=Item.objects.get(name='Gneiss'), material=Tritanium, quantity=171, activity=Refine).save()
Material(item=Item.objects.get(name='Gneiss'), material=Mexallon, quantity=171, activity=Refine).save()
Material(item=Item.objects.get(name='Gneiss'), material=Isogen, quantity=343, activity=Refine).save()
Material(item=Item.objects.get(name='Gneiss'), material=Zydrine, quantity=171, activity=Refine).save()
Material(item=Item.objects.get(name='Iridescent Gneiss'), material=Tritanium, quantity=180, activity=Refine).save()
Material(item=Item.objects.get(name='Iridescent Gneiss'), material=Mexallon, quantity=180, activity=Refine).save()
Material(item=Item.objects.get(name='Iridescent Gneiss'), material=Isogen, quantity=360, activity=Refine).save()
Material(item=Item.objects.get(name='Iridescent Gneiss'), material=Zydrine, quantity=180, activity=Refine).save()
Material(item=Item.objects.get(name='Prismatic Gneiss'), material=Tritanium, quantity=188, activity=Refine).save()
Material(item=Item.objects.get(name='Prismatic Gneiss'), material=Mexallon, quantity=188, activity=Refine).save()
Material(item=Item.objects.get(name='Prismatic Gneiss'), material=Isogen, quantity=377, activity=Refine).save()
Material(item=Item.objects.get(name='Prismatic Gneiss'), material=Zydrine, quantity=188, activity=Refine).save()

# Tritanium, Nocxium, Zydrine
Material(item=Item.objects.get(name='Dark Ochre'), material=Tritanium, quantity=250, activity=Refine).save()
Material(item=Item.objects.get(name='Dark Ochre'), material=Nocxium, quantity=500, activity=Refine).save()
Material(item=Item.objects.get(name='Dark Ochre'), material=Zydrine, quantity=250, activity=Refine).save()
Material(item=Item.objects.get(name='Onyx Ochre'), material=Tritanium, quantity=263, activity=Refine).save()
Material(item=Item.objects.get(name='Onyx Ochre'), material=Nocxium, quantity=525, activity=Refine).save()
Material(item=Item.objects.get(name='Onyx Ochre'), material=Zydrine, quantity=263, activity=Refine).save()
Material(item=Item.objects.get(name='Obsidian Ochre'), material=Tritanium, quantity=275, activity=Refine).save()
Material(item=Item.objects.get(name='Obsidian Ochre'), material=Nocxium, quantity=550, activity=Refine).save()
Material(item=Item.objects.get(name='Obsidian Ochre'), material=Zydrine, quantity=275, activity=Refine).save()

# Tritanium, Nocxium, Zydrine
Material(item=Item.objects.get(name='Crokite'), material=Tritanium, quantity=331, activity=Refine).save()
Material(item=Item.objects.get(name='Crokite'), material=Nocxium, quantity=331, activity=Refine).save()
Material(item=Item.objects.get(name='Crokite'), material=Zydrine, quantity=663, activity=Refine).save()
Material(item=Item.objects.get(name='Sharp Crokite'), material=Tritanium, quantity=348, activity=Refine).save()
Material(item=Item.objects.get(name='Sharp Crokite'), material=Nocxium, quantity=348, activity=Refine).save()
Material(item=Item.objects.get(name='Sharp Crokite'), material=Zydrine, quantity=696, activity=Refine).save()
Material(item=Item.objects.get(name='Crystalline Crokite'), material=Tritanium, quantity=364, activity=Refine).save()
Material(item=Item.objects.get(name='Crystalline Crokite'), material=Nocxium, quantity=364, activity=Refine).save()
Material(item=Item.objects.get(name='Crystalline Crokite'), material=Zydrine, quantity=729, activity=Refine).save()

# Pyerite, Zydrine, Megacyte
Material(item=Item.objects.get(name='Bistot'), material=Pyerite, quantity=170, activity=Refine).save()
Material(item=Item.objects.get(name='Bistot'), material=Zydrine, quantity=341, activity=Refine).save()
Material(item=Item.objects.get(name='Bistot'), material=Megacyte, quantity=170, activity=Refine).save()
Material(item=Item.objects.get(name='Triclinic Bistot'), material=Pyerite, quantity=179, activity=Refine).save()
Material(item=Item.objects.get(name='Triclinic Bistot'), material=Zydrine, quantity=358, activity=Refine).save()
Material(item=Item.objects.get(name='Triclinic Bistot'), material=Megacyte, quantity=179, activity=Refine).save()
Material(item=Item.objects.get(name='Monoclinic Bistot'), material=Pyerite, quantity=187, activity=Refine).save()
Material(item=Item.objects.get(name='Monoclinic Bistot'), material=Zydrine, quantity=375, activity=Refine).save()
Material(item=Item.objects.get(name='Monoclinic Bistot'), material=Megacyte, quantity=187, activity=Refine).save()

# Tritanium, Zydrine, Megacyte
Material(item=Item.objects.get(name='Arkonor'), material=Tritanium, quantity=300, activity=Refine).save()
Material(item=Item.objects.get(name='Arkonor'), material=Zydrine, quantity=166, activity=Refine).save()
Material(item=Item.objects.get(name='Arkonor'), material=Megacyte, quantity=333, activity=Refine).save()
Material(item=Item.objects.get(name='Crimson Arkonor'), material=Tritanium, quantity=315, activity=Refine).save()
Material(item=Item.objects.get(name='Crimson Arkonor'), material=Zydrine, quantity=174, activity=Refine).save()
Material(item=Item.objects.get(name='Crimson Arkonor'), material=Megacyte, quantity=350, activity=Refine).save()
Material(item=Item.objects.get(name='Prime Arkonor'), material=Tritanium, quantity=330, activity=Refine).save()
Material(item=Item.objects.get(name='Prime Arkonor'), material=Zydrine, quantity=183, activity=Refine).save()
Material(item=Item.objects.get(name='Prime Arkonor'), material=Megacyte, quantity=366, activity=Refine).save()

# Morphite
Material(item=Item.objects.get(name='Mercoxit'), material=Morphite, quantity=530, activity=Refine).save()
Material(item=Item.objects.get(name='Magma Mercoxit'), material=Morphite, quantity=557, activity=Refine).save()
Material(item=Item.objects.get(name='Vitreous Mercoxit'), material=Morphite, quantity=583, activity=Refine).save()

# Tritanium Pyerite Mexallon Isogen Nocxium Zydrine Megacyte Morphite
# Condensed Alloy
Material(item=Item.objects.get(name='Condensed Alloy'), material=Tritanium, quantity=88, activity=Refine).save()
Material(item=Item.objects.get(name='Condensed Alloy'), material=Pyerite, quantity=44, activity=Refine).save()
Material(item=Item.objects.get(name='Condensed Alloy'), material=Mexallon, quantity=11, activity=Refine).save()

# Crystal Compound
Material(item=Item.objects.get(name='Crystal Compound'), material=Mexallon, quantity=39, activity=Refine).save()
Material(item=Item.objects.get(name='Crystal Compound'), material=Isogen, quantity=2, activity=Refine).save()

# Precious Alloy
Material(item=Item.objects.get(name='Precious Alloy'), material=Pyerite, quantity=7, activity=Refine).save()
Material(item=Item.objects.get(name='Precious Alloy'), material=Isogen, quantity=18, activity=Refine).save()

# Gleaming Alloy
Material(item=Item.objects.get(name='Gleaming Alloy'), material=Tritanium, quantity=299, activity=Refine).save()
Material(item=Item.objects.get(name='Gleaming Alloy'), material=Nocxium, quantity=5, activity=Refine).save()

# Sheen Compound
Material(item=Item.objects.get(name='Sheen Compound'), material=Tritanium, quantity=124, activity=Refine).save()
Material(item=Item.objects.get(name='Sheen Compound'), material=Pyerite, quantity=44, activity=Refine).save()
Material(item=Item.objects.get(name='Sheen Compound'), material=Isogen, quantity=23, activity=Refine).save()
Material(item=Item.objects.get(name='Sheen Compound'), material=Nocxium, quantity=1, activity=Refine).save()

# Lucent Compound
Material(item=Item.objects.get(name='Lucent Compound'), material=Pyerite, quantity=174, activity=Refine).save()
Material(item=Item.objects.get(name='Lucent Compound'), material=Mexallon, quantity=2, activity=Refine).save()
Material(item=Item.objects.get(name='Lucent Compound'), material=Isogen, quantity=11, activity=Refine).save()
Material(item=Item.objects.get(name='Lucent Compound'), material=Nocxium, quantity=5, activity=Refine).save()

# Dark Compound
Material(item=Item.objects.get(name='Dark Compound'), material=Isogen, quantity=23, activity=Refine).save()
Material(item=Item.objects.get(name='Dark Compound'), material=Nocxium, quantity=10, activity=Refine).save()

# Motley Compound
Material(item=Item.objects.get(name='Motley Compound'), material=Isogen, quantity=28, activity=Refine).save()
Material(item=Item.objects.get(name='Motley Compound'), material=Nocxium, quantity=13, activity=Refine).save()

# Lustering Alloy
Material(item=Item.objects.get(name='Lustering Alloy'), material=Mexallon, quantity=88, activity=Refine).save()
Material(item=Item.objects.get(name='Lustering Alloy'), material=Isogen, quantity=32, activity=Refine).save()
Material(item=Item.objects.get(name='Lustering Alloy'), material=Nocxium, quantity=35, activity=Refine).save()
Material(item=Item.objects.get(name='Lustering Alloy'), material=Zydrine, quantity=2, activity=Refine).save()

# Plush Compound
Material(item=Item.objects.get(name='Plush Compound'), material=Pyerite, quantity=120, activity=Refine).save()
Material(item=Item.objects.get(name='Plush Compound'), material=Isogen, quantity=20, activity=Refine).save()
Material(item=Item.objects.get(name='Plush Compound'), material=Zydrine, quantity=18, activity=Refine).save()

# Glossy Compound
Material(item=Item.objects.get(name='Glossy Compound'), material=Nocxium, quantity=4, activity=Refine).save()
Material(item=Item.objects.get(name='Glossy Compound'), material=Megacyte, quantity=6, activity=Refine).save()

# Opulent Compound
Material(item=Item.objects.get(name='Opulent Compound'), material=Morphite, quantity=2, activity=Refine).save()

Heavy_Water = Item.objects.get(name='Heavy Water')
Liquid_Ozone = Item.objects.get(name='Liquid Ozone')
Strontium_Clathrates = Item.objects.get(name='Strontium Clathrates')
Oxygen_Isotopes = Item.objects.get(name='Oxygen Isotopes')
Nitrogen_Isotopes = Item.objects.get(name='Nitrogen Isotopes')
Helium_Isotopes = Item.objects.get(name='Helium Isotopes')
Hydrogen_Isotopes = Item.objects.get(name='Hydrogen Isotopes')

# Blue Ice
Material(item=Item.objects.get(name='Blue Ice'), material=Heavy_Water, quantity=50, activity=Refine).save()
Material(item=Item.objects.get(name='Blue Ice'), material=Liquid_Ozone, quantity=25, activity=Refine).save()
Material(item=Item.objects.get(name='Blue Ice'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Blue Ice'), material=Oxygen_Isotopes, quantity=300, activity=Refine).save()

# Glacial Mass
Material(item=Item.objects.get(name='Glacial Mass'), material=Heavy_Water, quantity=50, activity=Refine).save()
Material(item=Item.objects.get(name='Glacial Mass'), material=Liquid_Ozone, quantity=25, activity=Refine).save()
Material(item=Item.objects.get(name='Glacial Mass'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Glacial Mass'), material=Hydrogen_Isotopes, quantity=300, activity=Refine).save()

# White Glaze
Material(item=Item.objects.get(name='White Glaze'), material=Heavy_Water, quantity=50, activity=Refine).save()
Material(item=Item.objects.get(name='White Glaze'), material=Liquid_Ozone, quantity=25, activity=Refine).save()
Material(item=Item.objects.get(name='White Glaze'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='White Glaze'), material=Nitrogen_Isotopes, quantity=300, activity=Refine).save()

# Clear Icicle
Material(item=Item.objects.get(name='Clear Icicle'), material=Heavy_Water, quantity=50, activity=Refine).save()
Material(item=Item.objects.get(name='Clear Icicle'), material=Liquid_Ozone, quantity=25, activity=Refine).save()
Material(item=Item.objects.get(name='Clear Icicle'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Clear Icicle'), material=Helium_Isotopes, quantity=300, activity=Refine).save()

# Pristine White Glaze
Material(item=Item.objects.get(name='Pristine White Glaze'), material=Heavy_Water, quantity=75, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine White Glaze'), material=Liquid_Ozone, quantity=40, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine White Glaze'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Pristine White Glaze'), material=Nitrogen_Isotopes, quantity=350, activity=Refine).save()

# Thick Blue Ice
Material(item=Item.objects.get(name='Thick Blue Ice'), material=Heavy_Water, quantity=75, activity=Refine).save()
Material(item=Item.objects.get(name='Thick Blue Ice'), material=Liquid_Ozone, quantity=40, activity=Refine).save()
Material(item=Item.objects.get(name='Thick Blue Ice'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Thick Blue Ice'), material=Oxygen_Isotopes, quantity=350, activity=Refine).save()

# Smooth Glacial Mass
Material(item=Item.objects.get(name='Smooth Glacial Mass'), material=Heavy_Water, quantity=75, activity=Refine).save()
Material(item=Item.objects.get(name='Smooth Glacial Mass'), material=Liquid_Ozone, quantity=40, activity=Refine).save()
Material(item=Item.objects.get(name='Smooth Glacial Mass'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Smooth Glacial Mass'), material=Hydrogen_Isotopes, quantity=350, activity=Refine).save()

# Enriched Clear Icicle
Material(item=Item.objects.get(name='Enriched Clear Icicle'), material=Heavy_Water, quantity=75, activity=Refine).save()
Material(item=Item.objects.get(name='Enriched Clear Icicle'), material=Liquid_Ozone, quantity=40, activity=Refine).save()
Material(item=Item.objects.get(name='Enriched Clear Icicle'), material=Strontium_Clathrates, quantity=1, activity=Refine).save()
Material(item=Item.objects.get(name='Enriched Clear Icicle'), material=Helium_Isotopes, quantity=350, activity=Refine).save()

# Krystallos
Material(item=Item.objects.get(name='Krystallos'), material=Heavy_Water, quantity=100, activity=Refine).save()
Material(item=Item.objects.get(name='Krystallos'), material=Liquid_Ozone, quantity=250, activity=Refine).save()
Material(item=Item.objects.get(name='Krystallos'), material=Strontium_Clathrates, quantity=100, activity=Refine).save()

# Gelidus
Material(item=Item.objects.get(name='Gelidus'), material=Heavy_Water, quantity=250, activity=Refine).save()
Material(item=Item.objects.get(name='Gelidus'), material=Liquid_Ozone, quantity=500, activity=Refine).save()
Material(item=Item.objects.get(name='Gelidus'), material=Strontium_Clathrates, quantity=75, activity=Refine).save()

# Glare crust
Material(item=Item.objects.get(name='Glare crust'), material=Heavy_Water, quantity=1000, activity=Refine).save()
Material(item=Item.objects.get(name='Glare crust'), material=Liquid_Ozone, quantity=500, activity=Refine).save()
Material(item=Item.objects.get(name='Glare crust'), material=Strontium_Clathrates, quantity=25, activity=Refine).save()

# Dark glitter
Material(item=Item.objects.get(name='Dark glitter'), material=Heavy_Water, quantity=500, activity=Refine).save()
Material(item=Item.objects.get(name='Dark glitter'), material=Liquid_Ozone, quantity=1000, activity=Refine).save()
Material(item=Item.objects.get(name='Dark glitter'), material=Strontium_Clathrates, quantity=50, activity=Refine).save()

# Material(item=Item.objects.get(name='XXXX'), material=XXXX, quantity=0000, activity=Refine).save()
