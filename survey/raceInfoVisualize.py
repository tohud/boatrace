#!/usr/bin/env python
# coding: utf-8

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


# In[6]:


# 疎通
raceDate_t = "20180101"
with dbh.cursor() as cursor:
    sel_sql = "SELECT raceId FROM racemanagement                WHERE raceDate='%s' and racebeforeinfo_flg = TRUE"                 % (raceDate_t)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    print(raceIdList[0]['raceId'])


# In[ ]:





# In[8]:


with dbh.cursor() as cursor:
    sel_sql = "select * from raceresultsummary_v                where raceDate between '%s' and '%s' "               % (analyzeStartDate,analyzeEndDate)
    cursor.execute(sel_sql)
    raceInfoList=cursor.fetchall()
print(len(raceInfoList))


# In[9]:


df = pd.io.json.json_normalize(raceInfoList)
df.head()


# In[45]:


# 的中オッズの頻度分布
df['odds'].plot(kind='hist',bins=np.logspace(0,3,100))


# In[34]:


# 水面温度の頻度分布
df['raceSurfaceTemperature'].plot(kind='hist')


# In[38]:


# 波高の頻度分布
df['raceWaveHeight'].plot(kind='hist')


# In[41]:


# 風速の分布
df['raceWindSpeed'].plot(kind='hist')


# In[42]:


# メモリ使用チェック
print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
print(" ------------------------------------ ")
for var_name in dir():
    if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 1000: #ここだけアレンジ
        print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))


# In[3]:





# In[ ]:




