from django.db import models
from django.contrib.auth.models import User
from eve.ccp.models import Item

# Create your models here.
class MiningOp(models.Model):
    datetime = models.DateTimeField()
    description = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User)
    
    class Admin:
        pass
    
    class Meta:
        pass
    
    def __str__(self):
        if self.description:
            return "%s: %s" % (self.datetime, self.description)
        else:
            return "Mining Op #%s: %s" % (self.id, self.datetime)
        
    @property
    def name(self):
        return self.description

class MiningOpPhase(models.Model):
    operation = models.ForeignKey(MiningOp, related_name='phases',
                                  num_extra_on_change = 4)
    description = models.CharField(max_length=200, blank=True)
    shares = models.FloatField(editable=False, default=0)
    
    class Admin:
        list_display = ['id', 'operation', 'description', 'shares']
    
    def __str__(self):
        return "Mining Op Phase: %s: %s" % (self.datetime, self.longdesc)
    
    @property
    def datetime(self):
        return self.operation.datetime
    
    @property
    def longdesc(self):
        return "%s: %s" % (self.operation.description, self.description)
    
    @property
    def sharesizelist(self):
        list = [{'type':x.type, 'quantity':float(x.quantity)/self.shares} for x in self.ores.all()]
        return list
    
    @property
    def sharesizedict(self):
        return dict([ (x['type'], x['quantity']/self.shares) for x in self.ores.all() ])
    
class MinerOnOp(models.Model):
    phase = models.ForeignKey(MiningOpPhase, related_name='miners',
                              min_num_in_admin = 10,
                              num_extra_on_change = 4, 
                              edit_inline = models.TABULAR)
    user = models.ForeignKey(User, core=True)
    share = models.FloatField(default=1.0)

    class Admin:
        list_display = ['id', 'phase', 'user', 'share',]
        ordering = ['phase']
    
    def __str__(self):
        return "%s [%1.1f]: %s" % (self.user, self.share, self.phase.longdesc)
    
    def save(self):
        super(MinerOnOp, self).save() # Call the "real" save() method.

        # Update the current balance.
        # (We do it like this so edits don't make -very- odd things happen.
        shares = 0
        for row in self.phase.miners.all():
            shares += row.share
        self.phase.shares = shares
        self.phase.save()
    
class MiningOpOre(models.Model):
    phase = models.ForeignKey(MiningOpPhase, related_name='ores',
                              num_extra_on_change = 4,
                              min_num_in_admin = 6,
                              edit_inline = models.TABULAR)
    type = models.ForeignKey(Item, limit_choices_to = {'group__category__name':'Asteroid', 'published':True},
                             core=True)
    quantity = models.IntegerField()
    
    class Admin:
        list_display = ['id', 'phase', 'type', 'quantity']
        
    def __str__(self):
        return "%s: %s x%d" % (self.phase, self.type, self.quantity)
