import os
import django
import sys
sys.path.append("C:/Users/Nam/Desktop/All/projects/python projects/news_scraper/news_scraper/")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_scraper.settings')
django.setup()
from scraper.models import News
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from transformers import pipeline
import pymysql
import re

summarizer = pipeline('summarization')
max_chunk = 250

now = datetime.now()

########################################### GUARDIAN ##################################################
source_guardian = requests.get("https://www.theguardian.com/environment/all").text
soup_guardian = BeautifulSoup(source_guardian, "lxml")

#todays date - guardian
date_guardian = now.strftime("%#d-%B-%Y").lower()

print("---------- GUARDIAN ----------")
section_guardian = soup_guardian.find("section", {"id": date_guardian})

try:
  for article in section_guardian.find_all("a", class_="u-faux-block-link__overlay js-headline-text"):
    try:
      #title
      title_guardian = article.text
      #link
      href_guardian = article.get("href")
      #scrape each article
      source_articles_guardian = requests.get(href_guardian).text
      soup_article_guardian = BeautifulSoup(source_articles_guardian, "lxml")
      contents_guardian = soup_article_guardian.find("div", { "id" : "maincontent" })
      words_guardian = []
      for p in contents_guardian.find_all("p"):
        words_guardian.append(p.text)
      final_content_guardian = " ".join(map(str, words_guardian))
      
      #identify eos's
      final_content_guardian = final_content_guardian.replace('.', '.<eos>')
      final_content_guardian = final_content_guardian.replace('?', '?<eos>')
      final_content_guardian = final_content_guardian.replace('!', '!<eos>')

      #create chunks of sentences
      sentences_guardian = final_content_guardian.split('<eos>')
      current_chunk_guardian = 0 
      chunks_guardian = []
      for sentence_guardian in sentences_guardian:
          if len(chunks_guardian) == current_chunk_guardian + 1: 
              if len(chunks_guardian[current_chunk_guardian]) + len(sentence_guardian.split(' ')) <= max_chunk:
                  chunks_guardian[current_chunk_guardian].extend(sentence_guardian.split(' '))
              else:
                  current_chunk_guardian += 1
                  chunks_guardian.append(sentence_guardian.split(' '))
          else:
              chunks_guardian.append(sentence_guardian.split(' '))
      for chunk_id_guardian in range(len(chunks_guardian)):
          chunks_guardian[chunk_id_guardian] = ' '.join(chunks_guardian[chunk_id_guardian])
      
      #summarize chunks
      summary_guardian = summarizer(chunks_guardian, max_length=75, min_length=30, do_sample=False)
      summary_guardian_text = ' '.join([summ['summary_text'] for summ in summary_guardian])
      
      #insert into database
      News.objects.update_or_create(source="Guardian", headline=title_guardian, link=href_guardian, content=final_content_guardian, summary=summary_guardian_text)
    except Exception as e:
      pass
except Exception as e:
  pass


########################################### BBC ##################################################
source_bbc = requests.get("https://www.bbc.com/news/topics/c4y3wxdx24nt/our-planet-now").text
soup_bbc = BeautifulSoup(source_bbc, "lxml")

#todays date - bbc
#date_bbc = now.strftime("%#d %b")
print("---------- BBC ----------")
list_bbc = soup_bbc.find("ol", class_="gs-u-m0 gs-u-p0 lx-stream__feed qa-stream")
try:
  for articles in list_bbc.find_all("article"):
    try:
      posted_bbc = articles.find("span", class_="qa-post-auto-meta").text.split(" ",1)
      if len(posted_bbc) == 1: #identifies todays posts
        title_bbc = articles.find("a", class_="qa-heading-link lx-stream-post__header-link").text
        href_bbc = f"https://www.bbc.com{articles.a.get('href')}"
        source_articles_bbc = requests.get(href_bbc).text
        soup_article_bbc = BeautifulSoup(source_articles_bbc, "lxml")
        contents_bbc = soup_article_bbc.find("main", { "id" : "main-content" })
        contents_bbc_article = contents_bbc.find("article")
        words_bbc = []
        for p in contents_bbc_article.find_all("p", class_="ssrcss-1q0x1qg-Paragraph eq5iqo00"):
          words_bbc.append(p.text)
        final_content_bbc = " ".join(map(str, words_bbc))
        final_content_bbc = final_content_bbc.replace('.', '.<eos>')
        final_content_bbc = final_content_bbc.replace('?', '?<eos>')
        final_content_bbc = final_content_bbc.replace('!', '!<eos>')

        sentences_bbc = final_content_bbc.split('<eos>')
        current_chunk_bbc = 0 
        chunks_bbc = []
        for sentence_bbc in sentences_bbc:
            if len(chunks_bbc) == current_chunk_bbc + 1: 
                if len(chunks_bbc[current_chunk_bbc]) + len(sentence_bbc.split(' ')) <= max_chunk:
                    chunks_bbc[current_chunk_bbc].extend(sentence_bbc.split(' '))
                else:
                    current_chunk_bbc += 1
                    chunks_bbc.append(sentence_bbc.split(' '))
            else:
                chunks_bbc.append(sentence_bbc.split(' '))

        for chunk_id_bbc in range(len(chunks_bbc)):
            chunks_bbc[chunk_id_bbc] = ' '.join(chunks_bbc[chunk_id_bbc])

        summary_bbc = summarizer(chunks_bbc, max_length=75, min_length=30, do_sample=False)
        summary_bbc_text = ' '.join([summ['summary_text'] for summ in summary_bbc])
        #insert in database
        News.objects.update_or_create(source="bbc", headline=title_bbc, link=href_bbc, content=final_content_bbc, summary=summary_bbc_text) 
    except Exception as e:
      pass
except Exception as e:
  pass 


########################################### REUTERS ##################################################
source_reuters = requests.get("https://www.reuters.com/business/environment/").text
soup_reuters = BeautifulSoup(source_reuters, "lxml")

print("---------- REUTERS ----------")
try:
  section_reuters = soup_reuters.find("ul", class_="static-media-maximizer__cards__3HlXi static-media-maximizer__list__23N8R")
  for links in section_reuters.find_all("li"):
      posted_reuters = links.find("time").text.split(" ")
      if "AM" in posted_reuters or "PM" in posted_reuters:
        title_reuters = links.find("a", class_="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 heading__base__2T28j heading__heading_6__RtD9P media-story-card__heading__eqhp9").text
        part_reuters = links.find("a", class_="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 heading__base__2T28j heading__heading_6__RtD9P media-story-card__heading__eqhp9").get('href')
        href_reuters = f"https://www.reuters.com{part_reuters}"
        source_articles_reuters = requests.get(href_reuters).text
        soup_article_reuters = BeautifulSoup(source_articles_reuters, "lxml")
        regex = re.compile('.*paywall-article.*')
        contents_reuters = soup_article_reuters.find("div", { "class" : regex })

        words_reuters = []
        for p in contents_reuters.find_all("p"):
          words_reuters.append(p.text)
        final_content_reuters = " ".join(map(str, words_reuters))
        final_content_reuters = final_content_reuters.replace('.', '.<eos>')
        final_content_reuters = final_content_reuters.replace('?', '?<eos>')
        final_content_reuters = final_content_reuters.replace('!', '!<eos>')

        sentences_reuters = final_content_reuters.split('<eos>')
        current_chunk_reuters = 0 
        chunks_reuters = []
        for sentence_reuters in sentences_reuters:
            if len(chunks_reuters) == current_chunk_reuters + 1: 
                if len(chunks_reuters[current_chunk_reuters]) + len(sentence_reuters.split(' ')) <= max_chunk:
                    chunks_reuters[current_chunk_reuters].extend(sentence_reuters.split(' '))
                else:
                    current_chunk_reuters += 1
                    chunks_reuters.append(sentence_reuters.split(' '))
            else:
                chunks_reuters.append(sentence_reuters.split(' '))

        for chunk_id_reuters in range(len(chunks_reuters)):
            chunks_reuters[chunk_id_reuters] = ' '.join(chunks_reuters[chunk_id_reuters])

        summary_reuters = summarizer(chunks_reuters, max_length=75, min_length=30, do_sample=False)
        summary_reuters_text = ' '.join([summ['summary_text'] for summ in summary_reuters])
        #insert in database
        News.objects.update_or_create(source="Reuters", headline=title_reuters, link=href_reuters, content=final_content_reuters, summary=summary_reuters_text)
except Exception as e:
  pass  
