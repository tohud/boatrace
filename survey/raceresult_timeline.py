#!/usr/bin/env python
# coding: utf-8

# In[1]:


# todo:同じ人で連対率はどのくらい変わるのかを可視化する。
# todo:過去の連対率とその後の成績が実際に相関するのかを可視化する。
# warn:いずれも、枠によってバイアスがかからないように注意する。


# In[2]:


# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


# In[3]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[4]:


# 分析期間の指定は一旦ここでまとめてみる。
analyzeStartDate="20180101"
analyzeEndDate="20180131"


# In[5]:


dbh=dbHandler.getDBHandle()


# In[9]:


with dbh.cursor() as cursor:
    sel_sql = "select tm.raceId,tr.goalRank,tr.lane from raceresult tr,racemanagement tm                where tr.toban = '4406'                and tm.raceDate between '%s' and '%s'                and tr.raceId = tm.raceId                order by tr.raceId desc"                 % (analyzeStartDate,analyzeEndDate)
    cursor.execute(sel_sql)
    List=cursor.fetchall()
    print(List)
    


# In[ ]:




