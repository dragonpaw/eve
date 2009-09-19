from datetime import datetime, timedelta
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.core import cache
import re

from eve.lib.formatting import NavigationElement
from eve.lib.jinja import render_to_response
from eve.user.models import Character
from eve.pos.models import PlayerStation
from eve import settings

debug_nav = NavigationElement(
    "Debug", "/debug/", '06_04', 'The inner workings of the Widget.'
)
debug_request_nav = NavigationElement(
    "Request/Browser", "/debug/request/", None, 'Tell me about this browser.'
)
debug_loader_nav = NavigationElement(
    "Loader Schedule", "/debug/loader/", None, 'See upcoming loader job distribution.'
)
debug_memcache_nav = NavigationElement(
    "Memcached", "/debug/memcached/", None, 'Memcached statistics.'
)
@staff_member_required
def debug_menu(request):

    inline = [debug_loader_nav, debug_request_nav, debug_memcache_nav]
    nav = [debug_nav]

    d = {'inline_nav': inline, 'nav': nav}
    return render_to_response('generic_menu.html', d, request)

@staff_member_required
def debug_request(request):
    d = {}
    d['request'] = request
    d['nav'] = [debug_nav, debug_request_nav]
    meta = request.META.keys()
    meta.sort()
    d['meta'] = [(x, request.META[x]) for x in meta]

    return render_to_response('debug_request.html', d, request)

@staff_member_required
def debug_loader(request):
    d = {}

    poses = {}
    d['poses'] = poses
    d['nav'] = [debug_nav, debug_loader_nav]

    now = datetime.utcnow()
    now = now - timedelta(seconds=now.second)
    zero = timedelta(0)

    total_poses = PlayerStation.objects.count()
    for p in PlayerStation.objects.all():
        remain = p.cached_until - now
        if remain > zero:
            mins = remain.seconds / 60
        else:
            mins = 0
        if poses.has_key(mins):
            poses[mins] += 1
        else:
            poses[mins] = 1

    chars = {}
    d['chars'] = chars

    total_chars = 0
    for c in Character.objects.all():
        if c.user.is_stale:
            continue
        total_chars += 1

        remain = c.cached_until - now
        if remain > zero:
            mins = remain.seconds / 60
        else:
            mins = 0
        if chars.has_key(mins):
            chars[mins] += 1
        else:
            chars[mins] = 1

    d['total_poses'] = total_poses
    d['total_chars'] = total_chars

    return render_to_response('debug_loader.html', d, request)

@staff_member_required
def memcached(request):

    stats = cache.cache._cache.get_stats()

    return render_to_response(
        'debug_memcached.html', dict(
            stats=stats,
            nav = (debug_nav, debug_memcache_nav),
            time=datetime.now(), # server time
        ))