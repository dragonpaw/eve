#!/usr/bin/env python
import logging
from django_extensions.management.jobs import BaseJob as BaseJob_

class BaseJob(BaseJob_):

    def logger(self):
        return logging.getLogger(self.__module__)