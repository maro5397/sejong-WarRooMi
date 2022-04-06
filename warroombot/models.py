from django.db import models


class Booking(models.Model):
    studentnum = models.CharField(max_length=8)
    starttime = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    endtime = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    date = models.DateField(auto_now=False, auto_now_add=False) #%Y-%m-%d
    count = models.IntegerField()
    name = models.TextField()
    content = models.TextField()

class Forbid(models.Model):
    starttime = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    endtime = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    dayofweek = models.CharField(max_length=3)
    
class Calendar(models.Model):
    calendarpic = models.ImageField(upload_to='images/',blank=True, null=True)
    inittime = models.DateTimeField()