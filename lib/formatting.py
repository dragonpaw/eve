from django.template.defaultfilters import slugify
import logging

class NavigationElement:
    def __init__(self, name, url, icon, note=None, id=None):
        self.log = logging.getLogger('eve.lib.formatting.NavigationElement')
        self.log.info('Initializing new NavElement: %s', name)

        from eve.ccp.models import get_graphic
        if icon is None:
            graphic = get_graphic('09_14')
        else:
            graphic = get_graphic(icon)

        self.url = url
        self.name = name
        self.graphic = graphic
        self.note = note
        self.id = id
        self.icons = {}
        if self.graphic:
            self.log.debug('Caching icons.')
            for size in (16, 32, 64, 128):
                self.icons[size] = self.graphic.get_icon(size)

    def get_absolute_url(self):
        if self.id:
            return self.url % self.id
        else:
            return self.url

    def get_icon(self, size):
        if self.graphic is None:
            self.log.debug('Returning None graphic.')
            return None
        else:
            self.log.debug('Returning cached graphic.')
            return self.icons[size]

    @property
    def icon32(self):
        return self.get_icon(32)

    @property
    def icon64(self):
        return self.get_icon(64)

    def __getitem__(self, key):
        value = getattr(self, key)()
        return value

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
