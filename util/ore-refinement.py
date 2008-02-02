#!/usr/bin/env python
# $Id$

import os
import sys
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

Heavy_Water = Item.objects.get(name='Heavy Water')
Liquid_Ozone = Item.objects.get(name='Liquid Ozone')
Strontium_Clathrates = Item.objects.get(name='Strontium Clathrates')
Oxygen_Isotopes = Item.objects.get(name='Oxygen Isotopes')
Nitrogen_Isotopes = Item.objects.get(name='Nitrogen Isotopes')
Helium_Isotopes = Item.objects.get(name='Helium Isotopes')
Hydrogen_Isotopes = Item.objects.get(name='Hydrogen Isotopes')

ores = {
    # Tritanium
    'Veldspar':              { Tritanium: 1000 },
    'Concentrated Veldspar': { Tritanium: 1050 },
    'Dense Veldspar':        { Tritanium: 1100 },
    'Compressed Veldspar':              { Tritanium: 500000 },
    'Compressed Concentrated Veldspar': { Tritanium: 525000 },
    'Compressed Dense Veldspar':        { Tritanium: 550000 },

    # Tritanium, Pyerite
    'Scordite':           { Tritanium: 833, Pyerite: 416 },
    'Condensed Scordite': { Tritanium: 875, Pyerite: 437 }, 
    'Massive Scordite':   { Tritanium: 916, Pyerite: 458 }, 
    'Compressed Scordite':           { Tritanium: 249900, Pyerite: 124800 },
    'Compressed Condensed Scordite': { Tritanium: 262500, Pyerite: 131100 }, 
    'Compressed Massive Scordite':   { Tritanium: 274800, Pyerite: 137400 }, 
    
    # Tritanium, Pyerite, Mexallon, Nocxium
    'Pyroxeres':         { Tritanium: 844, Pyerite: 59, Mexallon: 120, Nocxium: 11 }, 
    'Solid Pyroxeres':   { Tritanium: 886, Pyerite: 62, Mexallon: 126, Nocxium: 12 },
    'Viscous Pyroxeres': { Tritanium: 928, Pyerite: 65, Mexallon: 132, Nocxium: 12 },
    'Compressed Pyroxeres':         { Tritanium: 126600, Pyerite: 8850, Mexallon: 18000, Nocxium: 1650 }, 
    'Compressed Solid Pyroxeres':   { Tritanium: 132900, Pyerite: 9300, Mexallon: 18900, Nocxium: 1800 },
    'Compressed Viscous Pyroxeres': { Tritanium: 139200, Pyerite: 9750, Mexallon: 19800, Nocxium: 1800 },
    
    # Tritanium, Pyerite, Mexallon
    'Plagioclase':       { Tritanium: 256, Pyerite: 512, Mexallon: 256 }, 
    'Azure Plagioclase': { Tritanium: 269, Pyerite: 538, Mexallon: 269 }, 
    'Rich Plagioclase':  { Tritanium: 282, Pyerite: 563, Mexallon: 282 }, 
    'Compressed Plagioclase':       { Tritanium: 25600, Pyerite: 51200, Mexallon: 25600 }, 
    'Compressed Azure Plagioclase': { Tritanium: 26900, Pyerite: 53800, Mexallon: 26900 }, 
    'Compressed Rich Plagioclase':  { Tritanium: 28200, Pyerite: 56300, Mexallon: 28200 }, 
    
    # Tritanium, Pyerite, Isogen
    'Omber':         { Tritanium: 307, Pyerite: 123, Isogen: 307 },
    'Silvery Omber': { Tritanium: 322, Pyerite: 129, Isogen: 322 },
    'Golden Omber':  { Tritanium: 338, Pyerite: 135, Isogen: 338 }, 
    'Compressed Omber':         { Tritanium: 15350, Pyerite: 6150, Isogen: 15350 },
    'Compressed Silvery Omber': { Tritanium: 16100, Pyerite: 6450, Isogen: 16100 },
    'Compressed Golden Omber':  { Tritanium: 16900, Pyerite: 6750, Isogen: 16900 }, 
    
    # Tritanium, Mexallon, Isogen
    'Kernite':          { Tritanium: 386, Mexallon: 773, Isogen: 386 }, 
    'Luminous Kernite': { Tritanium: 405, Mexallon: 812, Isogen: 405 }, 
    'Fiery Kernite':    { Tritanium: 425, Mexallon: 850, Isogen: 425 }, 
    'Compressed Kernite':          { Tritanium: 11580, Mexallon: 23190, Isogen: 11580 }, 
    'Compressed Luminous Kernite': { Tritanium: 12150, Mexallon: 24360, Isogen: 12150 }, 
    'Compressed Fiery Kernite':    { Tritanium: 12750, Mexallon: 25500, Isogen: 12750 }, 
    
    # Tritanium, Pyerite, Mexallon, Nocxium, Zydrine
    'Jaspet':          { Tritanium: 259, Pyerite: 259, Mexallon: 518, Nocxium: 259, Zydrine: 8 }, 
    'Pure Jaspet':     { Tritanium: 272, Pyerite: 272, Mexallon: 544, Nocxium: 272, Zydrine: 8 }, 
    'Pristine Jaspet': { Tritanium: 285, Pyerite: 285, Mexallon: 570, Nocxium: 285, Zydrine: 9 }, 
    'Compressed Jaspet':          { Tritanium: 3885, Pyerite: 3885, Mexallon: 7700, Nocxium: 3885, Zydrine: 120 }, 
    'Compressed Pure Jaspet':     { Tritanium: 4080, Pyerite: 4080, Mexallon: 8160, Nocxium: 4080, Zydrine: 120 }, 
    'Compressed Pristine Jaspet': { Tritanium: 4275, Pyerite: 4275, Mexallon: 8550, Nocxium: 4275, Zydrine: 135 },
    
    # Tritanium, Isogen, Nocxium, Zydrine
    'Hemorphite':         { Tritanium: 212, Isogen: 212, Nocxium: 424, Zydrine: 28 }, 
    'Vivid Hemorphite':   { Tritanium: 223, Isogen: 223, Nocxium: 445, Zydrine: 29 }, 
    'Radiant Hemorphite': { Tritanium: 233, Isogen: 233, Nocxium: 466, Zydrine: 31 }, 
    'Compressed Hemorphite':         { Tritanium: 2120, Isogen: 2120, Nocxium: 4240, Zydrine: 280 }, 
    'Compressed Vivid Hemorphite':   { Tritanium: 2230, Isogen: 2230, Nocxium: 4450, Zydrine: 290 }, 
    'Compressed Radiant Hemorphite': { Tritanium: 2330, Isogen: 2330, Nocxium: 4660, Zydrine: 310 }, 
    
    # Isogen, Nocxium, Zydrine
    'Hedbergite':        { Isogen: 708, Nocxium: 354, Zydrine: 32 }, 
    'Vitric Hedbergite': { Isogen: 743, Nocxium: 372, Zydrine: 34 }, 
    'Glazed Hedbergite': { Isogen: 779, Nocxium: 389, Zydrine: 35 }, 
    'Compressed Hedbergite':        { Isogen: 7080, Nocxium: 3540, Zydrine: 320 }, 
    'Compressed Vitric Hedbergite': { Isogen: 7430, Nocxium: 3720, Zydrine: 340 }, 
    'Compressed Glazed Hedbergite': { Isogen: 7790, Nocxium: 3890, Zydrine: 350 },
    
    # Tritanium, Pyerite, Megacyte
    'Spodumain':          { Tritanium: 700, Pyerite: 140, Megacyte: 140 }, 
    'Bright Spodumain':   { Tritanium: 735, Pyerite: 147, Megacyte: 147 }, 
    'Gleaming Spodumain': { Tritanium: 770, Pyerite: 154, Megacyte: 154 }, 
    'Compressed Spodumain':          { Tritanium: 3500, Pyerite: 700, Megacyte: 700 }, 
    'Compressed Bright Spodumain':   { Tritanium: 3675, Pyerite: 735, Megacyte: 735 }, 
    'Compressed Gleaming Spodumain': { Tritanium: 3850, Pyerite: 770, Megacyte: 770 }, 
    
    # Tritanium, Mexallon, Isogen, Zydrine
    'Gneiss':            { Tritanium: 171, Mexallon: 171, Isogen: 343, Zydrine: 171 }, 
    'Iridescent Gneiss': { Tritanium: 180, Mexallon: 180, Isogen: 360, Zydrine: 180 }, 
    'Prismatic Gneiss':  { Tritanium: 188, Mexallon: 188, Isogen: 377, Zydrine: 188 }, 
    'Compressed Gneiss':            { Tritanium: 1710, Mexallon: 1710, Isogen: 3430, Zydrine: 1710 }, 
    'Compressed Iridescent Gneiss': { Tritanium: 1800, Mexallon: 1800, Isogen: 3600, Zydrine: 1800 }, 
    'Compressed Prismatic Gneiss':  { Tritanium: 1880, Mexallon: 1880, Isogen: 3770, Zydrine: 1880 }, 
    
    # Tritanium, Nocxium, Zydrine
    'Dark Ochre':     { Tritanium: 250, Nocxium: 500, Zydrine: 250 }, 
    'Onyx Ochre':     { Tritanium: 263, Nocxium: 525, Zydrine: 263 }, 
    'Obsidian Ochre': { Tritanium: 275, Nocxium: 550, Zydrine: 275 }, 
    'Compressed Dark Ochre':     { Tritanium: 1250, Nocxium: 2500, Zydrine: 1250 }, 
    'Compressed Onyx Ochre':     { Tritanium: 1315, Nocxium: 2625, Zydrine: 1315 }, 
    'Compressed Obsidian Ochre': { Tritanium: 1375, Nocxium: 2750, Zydrine: 1375 }, 
    
    # Tritanium, Nocxium, Zydrine
    'Crokite':             { Tritanium: 331, Nocxium: 331, Zydrine: 663 }, 
    'Sharp Crokite':       { Tritanium: 348, Nocxium: 348, Zydrine: 696 }, 
    'Crystalline Crokite': { Tritanium: 364, Nocxium: 364, Zydrine: 729 }, 
    'Compressed Crokite':             { Tritanium: 1655, Nocxium: 1655, Zydrine: 3315 }, 
    'Compressed Sharp Crokite':       { Tritanium: 1740, Nocxium: 1740, Zydrine: 3480 }, 
    'Compressed Crystalline Crokite': { Tritanium: 1820, Nocxium: 1820, Zydrine: 3645 }, 
    
    # Pyerite, Zydrine, Megacyte
    'Bistot':            { Pyerite: 170, Zydrine: 341, Megacyte: 170 },
    'Triclinic Bistot':  { Pyerite: 179, Zydrine: 358, Megacyte: 179 }, 
    'Monoclinic Bistot': { Pyerite: 187, Zydrine: 375, Megacyte: 187 }, 
    'Compressed Bistot':            { Pyerite: 850, Zydrine: 1705, Megacyte: 850 },
    'Compressed Triclinic Bistot':  { Pyerite: 895, Zydrine: 1790, Megacyte: 895 }, 
    'Compressed Monoclinic Bistot': { Pyerite: 935, Zydrine: 1875, Megacyte: 935 }, 
    
    # Tritanium, Zydrine, Megacyte
    'Arkonor':         { Tritanium: 300, Zydrine: 166, Megacyte: 333 },
    'Crimson Arkonor': { Tritanium: 315, Zydrine: 174, Megacyte: 350 }, 
    'Prime Arkonor':   { Tritanium: 330, Zydrine: 183, Megacyte: 366 }, 
    'Compressed Arkonor':         { Tritanium: 1500, Zydrine: 830, Megacyte: 1665 }, 
    'Compressed Crimson Arkonor': { Tritanium: 1575, Zydrine: 870, Megacyte: 1750 }, 
    'Compressed Prime Arkonor':   { Tritanium: 1650, Zydrine: 915, Megacyte: 1830 }, 
    
    # Morphite
    'Mercoxit':          { Morphite: 530 }, 
    'Magma Mercoxit':    { Morphite: 557 }, 
    'Vitreous Mercoxit': { Morphite: 583 }, 
    'Compressed Mercoxit':          { Morphite: 1060 }, 
    'Compressed Magma Mercoxit':    { Morphite: 1114 }, 
    'Compressed Vitreous Mercoxit': { Morphite: 1166 }, 
    
    # Tritanium Pyerite Mexallon Isogen Nocxium Zydrine Megacyte Morphite
    'Condensed Alloy': { Tritanium: 88, Pyerite: 44, Mexallon: 11 }, 
    'Crystal Compound': { Mexallon: 39, Isogen: 2 },
    'Precious Alloy': { Pyerite: 7, Isogen: 18 },
    'Gleaming Alloy': { Tritanium: 299, Nocxium: 5 },
    'Sheen Compound': { Tritanium: 124, Pyerite: 44, Isogen: 23, Nocxium: 1 },
    'Lucent Compound': { Pyerite: 174, Mexallon: 2, Isogen: 11, Nocxium: 5 },
    'Dark Compound': { Isogen: 23, Nocxium: 10 },
    'Motley Compound': { Isogen: 28, Nocxium: 13 },
    'Lustering Alloy': { Mexallon: 88, Isogen: 32, Nocxium: 35, Zydrine: 1 },
    'Plush Compound': { Tritanium: 3200, Pyerite: 800, Isogen: 20, Zydrine: 9 },
    'Glossy Compound': { Nocxium: 4, Megacyte: 6 },
    'Opulent Compound': { Morphite: 2 },
    
    # Ices
    'Blue Ice':              { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Oxygen_Isotopes: 300 },
    'Glacial Mass':          { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Hydrogen_Isotopes: 300 },
    'White Glaze':           { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Nitrogen_Isotopes: 300 },
    'Clear Icicle':          { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Helium_Isotopes: 300 },
    'Pristine White Glaze':  { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Nitrogen_Isotopes: 350 },
    'Thick Blue Ice':        { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Oxygen_Isotopes: 350 },
    'Smooth Glacial Mass':   { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Hydrogen_Isotopes: 350 },
    'Enriched Clear Icicle': { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Helium_Isotopes: 350 },
    'Krystallos':            { Heavy_Water: 100, Liquid_Ozone: 250, Strontium_Clathrates: 100 },
    'Gelidus':               { Heavy_Water: 250, Liquid_Ozone: 500, Strontium_Clathrates: 75 },
    'Glare crust':           { Heavy_Water: 1000, Liquid_Ozone: 500, Strontium_Clathrates: 25 },
    'Dark glitter':          { Heavy_Water: 500, Liquid_Ozone: 1000, Strontium_Clathrates: 50 },
    'Compressed Blue Ice':              { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Oxygen_Isotopes: 300 },
    'Compressed Glacial Mass':          { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Hydrogen_Isotopes: 300 },
    'Compressed White Glaze':           { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Nitrogen_Isotopes: 300 },
    'Compressed Clear Icicle':          { Heavy_Water: 50, Liquid_Ozone: 25, Strontium_Clathrates: 1, Helium_Isotopes: 300 },
    'Compressed Pristine White Glaze':  { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Nitrogen_Isotopes: 350 },
    'Compressed Thick Blue Ice':        { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Oxygen_Isotopes: 350 },
    'Compressed Smooth Glacial Mass':   { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Hydrogen_Isotopes: 350 },
    'Compressed Enriched Clear Icicle': { Heavy_Water: 75, Liquid_Ozone: 40, Strontium_Clathrates: 1, Helium_Isotopes: 350 },
    'Compressed Krystallos':            { Heavy_Water: 100, Liquid_Ozone: 250, Strontium_Clathrates: 100 },
    'Compressed Gelidus':               { Heavy_Water: 250, Liquid_Ozone: 500, Strontium_Clathrates: 75 },
    'Compressed Glare crust':           { Heavy_Water: 1000, Liquid_Ozone: 500, Strontium_Clathrates: 25 },
    'Compressed Dark glitter':          { Heavy_Water: 500, Liquid_Ozone: 1000, Strontium_Clathrates: 50 },  
}

for orename in ores.keys():
    ore = Item.objects.get(name=orename)
    for mineral in ores[orename].keys():
        qty = ores[orename][mineral]
        print "%s refines into %d units of %s." % (ore, qty, mineral)
        Material(item=ore, material=mineral, quantity=qty, activity=Refine).save()
        
sys.exit(0)