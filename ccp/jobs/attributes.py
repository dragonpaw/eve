from django_extensions.management.jobs import BaseJob

from eve.ccp.models import Attribute, Graphic, AttributeCategory

class Job(BaseJob):
    help = "Create fake Attributes."
    when = 'once'

    def execute(self):
        portion = Attribute(id=5000)
        portion.attributename = 'portionsize'
        portion.category = AttributeCategory.objects.get(name='Structure')
        portion.description = 'Portion Size'
        portion.displayname = 'Portion Size'
        portion.published = True
        portion.defaultvalue = 1
        portion.graphic = Graphic.objects.get(icon='07_16')
        portion.save()

        print "Added: %s" % portion

        reprocessing = Attribute.objects.get(displayname='Reprocessing Skill')
        reprocessing.graphic = Graphic.objects.get(icon='50_13')
        reprocessing.category = AttributeCategory.objects.get(name='Required Skills')
        reprocessing.save()
        print "Changed: %s" % reprocessing
