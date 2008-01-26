import datetime
import re
from decimal import Decimal, InvalidOperation
from eve.ccp.models import icon32
import math

comma_regex = re.compile(r'^(-?\d+)(\d{3})')

def comma(num, separator=','):
    """commify(num, separator) -> string

    Return a string representing the number num with separator inserted
    for every power of 1000.   Separator defaults to a comma.
    E.g., commify(1234567) -> '1,234,567'
    """
    num = str(num)  # just in case we were passed a numeric value
    more_to_do = 1
    while more_to_do:
        (num, more_to_do) = comma_regex .subn(r'\1%s\2' % separator,num)
    return num

isk_map = (" kmbt")
def isk(isk):
    try:    
        isk = Decimal(str(isk))
    except InvalidOperation:
        return isk

    if isk == 0:
        return "0 ISK"
    else:
        floor = 1000
        value = abs(isk)
        for mag in isk_map:
            if value < floor:
                if isk/(floor/1000) > 100:
                    return "%0.0f%s" % (isk/(floor/1000), mag)
                elif isk/(floor/1000) > 10:
                    return "%0.1f%s" % (isk/(floor/1000), mag)
                else:
                    return "%0.2f%s" % (isk/(floor/1000), mag)
            else:
                floor *= 1000
        return isk

def time(sec):
    if isinstance(sec, datetime.timedelta):
        sec = sec.seconds + sec.days*86400
    try:
        sec = Decimal(str(sec))
    except InvalidOperation:
        return sec
        
    if sec < 60:
        return "%0.2f s" % sec
    elif sec < (60**2):
        return "%dm %ds" % (sec / 60, sec % 60)
    elif sec < (60**2 * 24):
        return "%dh %dm" % (sec / 60**2, sec % 60**2 / 60)
    else:
        return "%dd %dh" % (sec / (60**2*24), sec % (60**2*24) / 60**2)
   
def title(nav):
    temp = []
    for x in reversed(nav):
        if isinstance(x,dict):
            temp.append(x['name'])
        else:
            temp.append(x.name)
    return " &laquo; ".join(temp)
        

def make_nav(name, url, icon):
    if icon is not None:
        return {'name':name, 'get_absolute_url':url,'icon32':icon32(icon)}
    else:
        return {'name':name, 'get_absolute_url':url,'icon32':None}