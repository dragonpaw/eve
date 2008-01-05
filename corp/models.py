from django.db import models

class Alliance(models.Model):
    name = models.CharField(max_length=100)

# Create your models here.
class PlayerCorp(models.Model):
    name = models.CharField(max_length=100)
    alliance = models.ForeignKey(Alliance)