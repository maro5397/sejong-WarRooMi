from django.db import models


class Booking(models.Model):
    studentid = models.CharField(max_length=8)
    st = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M:%S
    et = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M:%S
    date = models.DateField(auto_now=False, auto_now_add=False) #%Y-%m-%d
    nos = models.IntegerField()
    name = models.TextField()
    ct = models.TextField()
    roomid = models.CharField(max_length=4)

class Forbid(models.Model):
    st = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    et = models.TimeField(auto_now=False, auto_now_add=False) #%H:%M
    dow = models.CharField(max_length=3)