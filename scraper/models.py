from django.db import models
from django.forms import DateTimeField

# Create your models here.


class News(models.Model):
  source = models.CharField(max_length=50)
  date = models.DateField(auto_now_add=True)
  headline = models.CharField(max_length=300)
  link = models.CharField(max_length=300)
  content = models.CharField(max_length=10000)
  summary = models.CharField(max_length=5000)

  def __str__(self):
    return self.headline
