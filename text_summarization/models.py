from cProfile import label
from django.db import models

# Create your models here.
class text(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    raw_text = models.CharField(max_length=10000)
    preprocessed_data = models.CharField(max_length=1000)
    summary = models.CharField(max_length=1000)
    labels = models.CharField(max_length=1000)
    