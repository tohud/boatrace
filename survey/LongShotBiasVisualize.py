#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ToDo LGBMの成果を評価するために、オッズ帯別の回収率を見てみる。

# 汎用ライブラリのimport
import sys
import os
import math
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


# In[2]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[3]:


# 分析期間の指定は一旦ここでまとめてみる。
analyzeStartDate="20180101"
analyzeEndDate="20190131"


# In[4]:


dbh=dbHandler.getDBHandle()


# In[5]:


# 疎通
raceDate_t = "20180101"
with dbh.cursor() as cursor:
    sel_sql = "SELECT raceId FROM racemanagement                WHERE raceDate='%s' and racebeforeinfo_flg = TRUE"                 % (raceDate_t)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    print(raceIdList[0]['raceId'])


# In[6]:


# オッズ帯は対数分布から作る。何段階にするかを指定する
oddsRankNum = 31
maxOddsVal = 9999
logMaxOddsVal=math.log(maxOddsVal)
oddsRankList=[]
for i in range(oddsRankNum):
    print( math.exp(logMaxOddsVal/oddsRankNum*i) )
    oddsRankList.append(math.exp(logMaxOddsVal/oddsRankNum*i))


# In[7]:


# オッズの分布
oddsRank_sql = ""
for i in range(oddsRankNum-1):
    oddsRank_sql += "count(CASE WHEN o.odds between %f and %f THEN 1 END ) rank%d ," % (oddsRankList[i],oddsRankList[i+1],i+1)
oddsRank_sql += "count(CASE WHEN o.odds > %f THEN 1 END ) rank%d " %(oddsRankList[oddsRankNum-1],oddsRankNum)
sel_sql = "select " + oddsRank_sql +"from raceodds o , racemanagement m            where o.raceId = m.raceId            and o.oddsType = '3t'            and m.raceDate between '%s' and '%s'"           % (analyzeStartDate,analyzeEndDate)
print(sel_sql)

with dbh.cursor() as cursor:
    cursor.execute(sel_sql)
    odds_dist=cursor.fetchall()[0]
print(odds_dist)


# In[8]:


# 回収金額の分布
returnRank_sql = ""
for i in range(oddsRankNum-1):
    returnRank_sql += "sum(CASE WHEN odds between %f and %f THEN odds*100 END ) rank%d ," % (oddsRankList[i],oddsRankList[i+1],i+1)
returnRank_sql += "sum(CASE WHEN odds > %f THEN odds*100 END ) rank%d " %(oddsRankList[oddsRankNum-1],oddsRankNum)
sel_sql = "select " + returnRank_sql +"from raceresultsummary_v            where raceDate between '%s' and '%s'"           % (analyzeStartDate,analyzeEndDate)
print(sel_sql)

with dbh.cursor() as cursor:
    cursor.execute(sel_sql)
    return_dist=cursor.fetchall()[0]
print(return_dist)


# In[9]:


# 回収率を見る
# 10倍未満の本命周辺で回収率は78%～81%くらい。これを安定的に超えられれば、一応有効といえる。
kaishuRank=[]
oddsNum_dist=[]
for r in odds_dist.keys():
    if odds_dist[r] == None:
        oddsNum_dist.append(0)
    else:
        oddsNum_dist.append(odds_dist[r])
    if return_dist[r] == None or odds_dist[r]== None:
        kaishuRank.append(0)
    else:
        kaishuRank.append(return_dist[r]/odds_dist[r])
plt.plot(kaishuRank)

print(kaishuRank)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[11]:


# メモリ使用チェック
print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
print(" ------------------------------------ ")
for var_name in dir():
    if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 1000: #ここだけアレンジ
        print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))


# In[ ]:





# In[ ]:




