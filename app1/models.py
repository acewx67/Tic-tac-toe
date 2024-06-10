from django.db import models

# Create your models here.
class Array(models.Model):
    data = models.JSONField(default=[None]*9)
    group_name = models.CharField(max_length=255,primary_key=True)
    