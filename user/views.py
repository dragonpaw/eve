from django.shortcuts import render_to_response
from django.template import RequestContext
from eve.util.formatting import make_nav

user_nav = make_nav("Characters", "/user/", '34_12')

def main(request):
    d = {}
    d['nav'] = [ user_nav ]  
    
    return render_to_response('user_main.html', d, context_instance=RequestContext(request))

