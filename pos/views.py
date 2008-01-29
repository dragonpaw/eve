#from django import newforms as forms
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.pos.models import PlayerStation
from eve.util.formatting import make_nav

pos_nav = make_nav("Player-owned Stations", "/pos/", '40_14', 
                   note='Fuel status for all of your POSes.')

def list(request):
    d = {}
    d['nav'] = [pos_nav]
    corps = {}
    
    for c in request.user.get_profile().characters.filter(is_director=True):
        poses = c.corporation.pos.select_related().order_by('solarsystem', 
                                                            'ccp_mapdenormalize.celestialindex',
                                                            'ccp_mapdenormalize.orbitindex',
                                                            )
        corps[c.corporation.name] = {
                                        'name':c.corporation.name,
                                        'pos':poses,
                                    }
    # = models.IntegerField(null=True, blank=True)
    #orbitindex)} 

    #t = t.order_by('ccp_category.categoryname','ccp_group.groupname','ccp_item.name')
    d['poses'] = corps.values() 
    
    return render_to_response('pos_station_list.html', d, context_instance=RequestContext(request))


def detail(request, station_id):
    pos = get_object_or_404(PlayerStation, id=station_id)
    
    d = {}
    d['nav'] = [pos_nav, pos]
    d['pos'] = pos
    
    return render_to_response('pos_station_detail.html', d, context_instance=RequestContext(request))