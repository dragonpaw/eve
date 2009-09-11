#!/usr/bin/env python

from django.db import models

# In EVE, everything can be null.
class Int(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        return super(Int, self).__init__(*args, **kwargs)

class Float(models.FloatField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        return super(Float, self).__init__(*args, **kwargs)

class Char(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        return super(Char, self).__init__(*args, **kwargs)

class Key(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        return super(Key, self).__init__(*args, **kwargs)

class Char(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        return super(Char, self).__init__(*args, **kwargs)

class Small(models.SmallIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        return super(Small, self).__init__(*args, **kwargs)
