from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

STATUS_CODES = (
    (1, 'Open'),
    (2, 'Working'),
    (3, 'Closed'),
    )

PRIORITY_CODES = (
    (1, 'Bug!'),
    (2, 'Enhancement Request'),
    (3, 'Wish List'),
    )

apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
PROJECTS = list(enumerate(apps))

class Ticket(models.Model):
    """Trouble tickets"""
    title = models.CharField(max_length=100)
    project = models.CharField(blank=True, max_length=100, choices=PROJECTS)
    submitted_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    submitter = models.ForeignKey(User, related_name="submitter")
    assigned_to = models.ForeignKey(User, limit_choices_to = {'is_staff': True})
    description = models.TextField(blank=True)
    status = models.IntegerField(default=1, choices=STATUS_CODES)
    priority = models.IntegerField(default=1, choices=PRIORITY_CODES)

    class Meta:
        ordering = ('status', 'priority', 'submitted_date', 'title')

    def __str__(self):
        return self.title

class ChangeLog(models.Model):
    """Changes made"""
    date = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        ordering = ('-date',)
