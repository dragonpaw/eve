from django.db import models
from django.contrib.auth.models import User
from eve.ccp.models import Item

# Create your models here.
class MiningOp(models.Model):
    datetime = models.DateTimeField()
    description = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User)
    hours = models.FloatField(editable=False, default=0)
    
    def __unicode__(self):
        if self.description:
            return u"%s: %s" % (self.datetime, self.description)
        else:
            return u"Mining Op #%s: %s" % (self.id, self.datetime)
        
    @property
    def name(self):
        return self.description
    
    def sharesizelist(self):
        list = [{'type':x.type, 'quantity':float(x.quantity)/self.shares} for x in self.ores.all()]
        return list
    
    @property
    def sharesizedict(self):
        return dict([ (x['type'], x['quantity']/self.shares) for x in self.ores.all() ])
    
class MinerOnOp(models.Model):
    op = models.ForeignKey(MiningOp, related_name='miners')
    name = models.CharField(max_length=100)
    multiplier = models.FloatField(default=1.0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def hours(self):
        x = self.end_time - self.start_time
        return (x.days * 24) + (x.seconds / 60.0**2)
    
    def percent(self):
        total_hours = self.op.hours
        return (self.hours() * self.multiplier) / total_hours
    
    def __unicode__(self):
        return u"%s [%1.2f]" % (self.name, self.hours())
    
    def save(self):
        super(MinerOnOp, self).save() # Call the "real" save() method.

        # Update the current balance.
        # (We do it like this so edits don't make -very- odd things happen.
        hours = 0
        for row in self.op.miners.all():
            hours += row.hours() * row.multiplier
        self.op.hours = hours
        self.op.save()
    
class MiningOpMineral(models.Model):
    op = models.ForeignKey(MiningOp, related_name='minerals')
    type = models.ForeignKey(Item, limit_choices_to = {'group__name':'Mineral', 'published':True})
    quantity = models.IntegerField()
    
    class Admin:
        list_display = ['id', 'op', 'type', 'quantity']
        
    def __unicode__(self):
        return u"%s: %s x%d" % (self.op, self.type, self.quantity)
