from eve.ccp.models import *

#print dir(Item)

def test_item_details():
    item = Item.objects.get(id=12818)
    assert( item.name == 'Scorch M' )
    assert( item.group.name == 'Advanced Pulse Laser Crystal' )
    assert( item.graphic.id == 1141 )
    assert( item.graphic.icon == "08_04" )

def test_item_blueprint_relation():
    item = Item.objects.get(id=24700) # Myrmidon
    assert( item.name == 'Myrmidon' )
    assert( item.blueprint.name == 'Myrmidon Blueprint' )
    assert( item.blueprint.id == 24701 )
    assert( item.blueprint.blueprint_details.techlevel == 1 )

    blueprint = Item.objects.get(id=24701) # Myrmidon Blueprint
    assert( blueprint.name == 'Myrmidon Blueprint' )
    assert( blueprint.blueprint_details.techlevel == 1 )

def test_materials():
    set = Material.objects.filter(item=24701, activity=1)
    for m in set:
        print m
    
def test_item_skills():
    skill = Item.objects.get(name='Empathy')
    assert( skill.skill_rank == 1 )
    skill = Item.objects.get(name='Deep Core Mining')
    assert( skill.skill_rank == 6 )
    not_skill = Item.objects.get(name='Antimatter Charge L')
    assert( not_skill.is_skill is False )
    
    for skill in Item.skill_objects.all():
        print skill
        assert( skill.is_skill is True )
    
def test_item_manafacturing_costs():
    i = Item.objects.get(name='Myrmidon')
    assert( type(i.materials) == list ) 
    for mat in i.materials:
        if mat[0].name == 'Tritanium':
            assert(mat[1] == 2885176)
            break
    else:
        assert(False) # Didn't find the Tritanium!
    
    mats = i.materials_by_name
    assert( type(mats) == dict )
    assert( mats['Tritanium'] == 2885176 )
    assert( mats['Nocxium']   ==   13483 )
    assert( mats['Pyerite']   ==  642378 )
    assert( mats['Zydrine']   ==    2523 )
    assert( mats['Mexallon']  ==  215466 )
    
