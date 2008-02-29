import datetime
import re
from decimal import Decimal, InvalidOperation
from django.template.defaultfilters import slugify

comma_regex = re.compile(r'^(-?\d+)(\d{3})')
def comma(num, separator=','):
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
def isk(isk):
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
   
def title(nav):
    temp = []
    for x in reversed(nav):
        if isinstance(x,dict):
            temp.append(x['name'])
        else:
            temp.append(x.name)
    return " &laquo; ".join(temp)
        
class NavigationElement:
    def __init__(self, name, url, icon=None, note=None, id=None):
        from eve.ccp.models import get_graphic
        if icon is not None:
            graphic = get_graphic(icon)
        else:
            graphic = None
            
        self.url = url
        self.name = name
        self.graphic = graphic
        self.note = note
        self.id = id
    
    def get_absolute_url(self):
        if self.id:
            return self.url % self.id
        else:
            return self.url
        
    def icon32(self):
        if self.graphic is None:
            return None
        else:
            return self.graphic.icon32

def make_nav(name, url, icon, note=None):
    return NavigationElement(name, url, icon, note=note, id=None)

def javascript_points(list):
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

def unique_slug(item,slug_source='name',slug_field='slug'):
    """unique_slug(item,slug_source='name',slug_field='slug')
    
    Ensures a unique slug field by appending an integer counter to duplicate 
    slugs.
  
    If the item already has a slug, then it is returned without modification
    or checking. If it does not have a slug, then one will be determined and
    returned.
    
    The item's slug field is first populated by slugify-ing the source field.
    If that value already exists, a counter is appended to the slug, and the 
    counter incremented upward until the value is unique.
  
    For instance, if you save an object titled Daily Roundup, and the slug 
    daily-roundup is already taken, this function will try daily-roundup-2, 
    daily-roundup-3, daily-roundup-4, etc, until a unique value is found.
  
    Call from within a model's custom save() method like so:
    item.slug = unique_slug(item)

    Default slug_source field is 'name'.
    Default slug_field name is 'slug'.
    """
    # if it's already got a slug, do nothing.
    slug = getattr(item, slug_field)
    if slug:
        return slug 
    
    slug = slugify(getattr(item,slug_source))
    
    slug_search = slug_field + '__istartswith'
    itemModel = item.__class__
    query = itemModel.objects.filter(**{slug_search:slug})
    
    # the following gets all existing slug values
    slugs = [x[slug_field] for x in query.values(slug_field)]
    test = slug

    counter = 1 # Increments to 2 if the slug is not unique
    while test in slugs:
        counter += 1
        test = "%s-%i" % (slug, counter)
    return test