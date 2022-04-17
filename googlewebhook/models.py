from django.db import models


class Forbid(models.Model):
    st = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    et = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    dow = models.CharField(max_length=3)