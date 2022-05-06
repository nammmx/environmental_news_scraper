from .models import News
from django import forms
import django_filters


class SourceFilter(django_filters.FilterSet):
  class Meta:
      model = News
      fields = ['source', ]