from django.db import models
class GameScores(models.Model):
    username = models.CharField(null=True, max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField()
    time_start = models.FloatField()
    time_end = models.FloatField()
    time_delta = models.FloatField()
    ip = models.IPAddressField()

class Words(models.Model):
    word = models.CharField(max_length=50)
    definition = models.CharField(max_length=200)
    speech = models.CharField(max_length=20)
