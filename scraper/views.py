from django.shortcuts import render
from .models import News
import requests
from datetime import datetime, timedelta
from .filters import SourceFilter


def home(request):
  news = News.objects.all().order_by("-date")
  source_filter = SourceFilter(request.GET, queryset=news)
  return render(request, "scraper/home.html", {"news":news, "filter":source_filter})