#!/usr/bin/env python
import math
import datetime
import re
from decimal import Decimal, InvalidOperation
import markdown

comma_regex = re.compile(r'^(-?\d+)(\d{3})')

def filter_time(sec):
    if isinstance(sec, datetime.timedelta):
        sec = sec.seconds + sec.days*86400
    try:
        sec = int(str(sec))
    except:
        return ''

    if sec < 60:
        return "%0.2f s" % sec
    elif sec < (60**2):
        if sec % 60 == 0:
            return "%dm" % (sec / 60)
        else:
            return "%dm %ds" % (sec / 60, sec % 60)
    elif sec < (60**2 * 24):
        if sec % 60**2 == 0:
            return "%dh" % (sec / 60**2)
        else:
            return "%dh %dm" % (sec / 60**2, sec % 60**2 / 60)
    else:
        return "%dd %dh" % (sec / (60**2*24), sec % (60**2*24) / 60**2)

def filter_navtitle(nav):
    temp = []
    for x in reversed(nav):
        if isinstance(x,dict):
            temp.append(x['name'])
        else:
            temp.append(x.name)
    return " &laquo; ".join(temp)

def filter_js_points(list):
    if isinstance(list, dict):
        buffer = []
        keys = list.keys()
        keys.sort()
        for x in keys:
            buffer.append('[%s, %s]' % (x, list[x]))
        return '[' + ', '.join(buffer) + ']'
    else:
        buffer = '[%s]' % ', '.join(['[%s]' % ', '.join(x) for x in list])
        return buffer

def filter_comma(num, separator=','):
    """comma(num, separator) -> string

    Return a string representing the number num with separator inserted
    for every power of 1000.   Separator defaults to a comma.
    E.g., commify(1234567) -> '1,234,567'
    """
    num = str(num)  # just in case we were passed a numeric value
    more_to_do = 1
    while more_to_do:
        (num, more_to_do) = comma_regex .subn(r'\1%s\2' % separator,num)
    return num

isk_map = (" kmbt") # kilo, million, billion, trillion...
def filter_isk(isk):
    """Take a integer value and return it in human representation with a suffix
    such as 'b' for billion.

    There will always be 3 significant digits in the results.

    Examples:
    '2.33k ISK' = isk(2330)
    '100k ISK'  = isk(100000)
    '12.2m ISK' = isk(12000000)
    """
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

def filter_floatformat(number, precision=-1):
    number = float(number) # Just to be sure. In case we're passed an int.
    if precision < 0 and math.floor(number) == number:
        return int(number)
    else:
        format = '%.' + str(abs(int(precision))) + 'f'
        return format % number

def filter_markdown(text):
    return markdown.markdown(text)

def filter_yesno(arg, yes, no):
    if arg:
        return yes
    else:
        return no
