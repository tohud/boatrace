#!/usr/bin/env python
# coding: utf-8

# In[55]:


# todo:同じ人で連対率はどのくらい変わるのかを可視化する。
# todo:過去の連対率とその後の成績が実際に相関するのかを可視化する。
# warn:いずれも、枠によってバイアスがかからないように注意する。


# In[56]:


# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm


# In[57]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[58]:


# 分析期間の指定は一旦ここでまとめてみる。
analyzeStartDate="20180101"
analyzeEndDate="20181231"


# In[59]:


dbh=dbHandler.getDBHandle()


# In[71]:


with dbh.cursor() as cursor:
    sel_sql = "select * from                ( select tm.raceId,tr.goalRank,tr.lane from raceresult tr,racemanagement tm                  where tr.toban = '4124'                  and tm.raceDate between '%s' and '%s'                  and tr.raceId = tm.raceId                  order by tr.raceId desc ) a                order by raceId asc "                 % (analyzeStartDate,analyzeEndDate)
    cursor.execute(sel_sql)
    resultList=cursor.fetchall()
    


# In[72]:


df = pd.io.json.json_normalize(resultList)
df.head()


# In[73]:


df_av5=df['goalRank'].rolling(5)
df_av5.mean()


# In[74]:


df['goalRank'].plot()
df_av5.mean().plot()


# In[75]:


# 自己相関係数を算出
acf = sm.tsa.stattools.acf(df['goalRank'], nlags=30)
print(acf)
pd.DataFrame(acf).plot()
df_av5_2= df_av5.mean().drop([i for i in range(5)])
acf = sm.tsa.stattools.acf(df_av5_2, nlags=30)
pd.DataFrame(acf).plot()
print(acf)


# In[ ]:




