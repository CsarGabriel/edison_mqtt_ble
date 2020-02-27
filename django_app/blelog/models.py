# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Device(models.Model):
    name = models.CharField(max_length = 80, default="Undefined_name")
    mac = models.CharField(max_length = 17)
    status = models.BooleanField()

    def __str__(self):
        return self.name + " -- " + self.mac

class Log(models.Model):
    timestamp = models.DecimalField(max_digits = 10, decimal_places = 0)
    event = models.CharField(max_length = 500)
    device = models.ForeignKey(Device, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.timestamp) + " -- " + self.event[:10] + "..." 

