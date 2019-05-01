#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 公式からとってくる。
# レースリスト、レースの参加メンバー、直前のオッズリストをDBに突っ込む
# https://www.boatrace.jp/owpc/pc/race/index?hd=%s
# mySQL接続用のユーザ、パスワードは $BR_HOME/config_nogit/mysqlUser.json

# ToDO raceinfoをとっておく
# ToDo 日付を期間指定にする
# ToDo テーブル間のリコンサイルをする

import os
from bs4 import BeautifulSoup
import json
import urllib.request as u
import time
import re
import elasticsearch as es

import unicodedata

import pymysql
from getDataFromKoushiki import getInfoKoushiki
from getDataFromKoushiki import setInfoKoushiki
from myUtil import dbHandler


# In[2]:


print(os.environ['GACRP_HOME'])
print(os.environ['BR_HOME'])


# In[3]:


dbh=dbHandler.getDBHandle()


# In[4]:


#dbHandler.closeDBHandle(dbh)


# In[5]:


#　会場とplaceIdとの紐づけファイルをロード。たぶん使わない。
with open('../config/def-place.json','r',encoding='utf8') as defPlace:
    placeDict=json.load(defPlace)
print(placeDict[0]['placeId'],placeDict[0]['placeName'])
#for i in range(len(placeDict)):
#    print("|"+placeDict[i]['placeId']+"|"+placeDict[i]['placeName']+"|")


# In[6]:


raceDate="20190323"


# In[7]:


# レースの一覧を取得し、足りないracemanegementを作る。
setInfoKoushiki.setRaceManagementKoushiki(dbh,raceDate)


# In[8]:


# racemanegementをもとに、レースの直前情報を取得する。
# ただし、beforeinfoはレースで一意の情報（Weather）と、メンバーごとの情報をわける。
dbh.rollback()
setInfoKoushiki.setRaceBeforeInfoWeatherKoushiki(dbh,raceDate)


# In[9]:


# racemanegementをもとに、レースのメンバー情報を取得する。
dbh.rollback()
setInfoKoushiki.setRaceMemberKoushiki(dbh,raceDate)


# In[10]:


# 3連単のオッズ情報を取得する
dbh.rollback()
setInfoKoushiki.setOldOddsKoushiki3rentan(dbh,raceDate)


# In[11]:


# 3連複のオッズ情報を取得する
dbh.rollback()
setInfoKoushiki.setOldOddsKoushiki3renfuku(dbh,raceDate)


# In[12]:


# 2連単のオッズ情報を取得する
dbh.rollback()
setInfoKoushiki.setOldOddsKoushiki2rentan(dbh,raceDate)


# In[13]:


# 2連複のオッズ情報を取得する
dbh.rollback()
setInfoKoushiki.setOldOddsKoushiki2renfuku(dbh,raceDate)


# In[14]:


# 単勝のオッズ情報を取得する
dbh.rollback()
setInfoKoushiki.setOldOddsKoushikiTansho(dbh,raceDate)


# In[15]:


# レース結果情報を取得する
dbh.rollback()
setInfoKoushiki.setOldOddsKoushikiResult(dbh,raceDate)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




