#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# バッチで過去のレース情報・オッズを取得する
# バッチ専用なので、jupyterで動かすときにはDebugをTrueにすること。⇒コード変えるの面倒なので引数なかったらDebugモードにする。
# args[1]:startDate  args[2]:endDate
# Usage: nohup python getOldOddsBatch.py startDate endDate > $BR_HOME/log/batch.log &
import os
from bs4 import BeautifulSoup
import json
import urllib.request as u
import time
import re
import sys
import datetime

import unicodedata

import pymysql
from getDataFromKoushiki import getInfoKoushiki
from getDataFromKoushiki import setInfoKoushiki
from myUtil import dbHandler


# In[2]:


args = sys.argv
if len(args)==0:
    Debug=True
else:
    Debug=False


# In[3]:


if Debug:
    startDate="20181220"
    endDate  ="20181221"
else:
    startDate=args[1]
    endDate=args[2]


# In[4]:


startDate_t=datetime.datetime.strptime(startDate,'%Y%m%d')
endDate_t  =datetime.datetime.strptime(endDate,'%Y%m%d')
raceDate_t=startDate_t

dbh=dbHandler.getDBHandle()
while raceDate_t <= endDate_t:
    raceDate=raceDate_t.strftime('%Y%m%d')
    print("START:"+raceDate)
    
    # レースの一覧を取得し、足りないracemanegementを作る。
    setInfoKoushiki.setRaceManagementKoushiki(dbh,raceDate)    
    # racemanegementをもとに、レースの直前情報を取得する。
    # ただし、beforeinfoはレースで一意の情報（Weather）と、メンバーごとの情報をわける。
    setInfoKoushiki.setRaceBeforeInfoWeatherKoushiki(dbh,raceDate)
    # racemanegementをもとに、レースのメンバー情報を取得する。
    setInfoKoushiki.setRaceMemberKoushiki(dbh,raceDate)    
    # 3連単のオッズ情報を取得する
    setInfoKoushiki.setOldOddsKoushiki3rentan(dbh,raceDate)
    # 3連複のオッズ情報を取得する
    setInfoKoushiki.setOldOddsKoushiki3renfuku(dbh,raceDate)
    # 2連単のオッズ情報を取得する
    setInfoKoushiki.setOldOddsKoushiki2rentan(dbh,raceDate)
    # 2連複のオッズ情報を取得する
    setInfoKoushiki.setOldOddsKoushiki2renfuku(dbh,raceDate)
    # 単勝のオッズ情報を取得する
    setInfoKoushiki.setOldOddsKoushikiTansho(dbh,raceDate)
    # レース結果情報を取得する
    setInfoKoushiki.setOldOddsKoushikiResult(dbh,raceDate)
    
    print("END:"+raceDate)    
    raceDate_t=raceDate_t+datetime.timedelta(days=1)


# In[ ]:




