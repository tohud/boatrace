#!/usr/bin/env python
# coding: utf-8

# In[6]:


# ToDo 

# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


# In[7]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[8]:


# 分析期間の指定は一旦ここでまとめてみる。
analyzeStartDate="20180101"
analyzeEndDate="20180131"


# In[9]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[14]:


# 日付と登録番号を与えて、該当選手の直近30回のスタート時刻の、各レース平均に対する偏差平均を出す。フライング除く。
# 現在は、各レース平均に対する偏差のリストを返している。
raceDate = "20180131"
toban="4337"
with dbh.cursor() as cursor:
    sel_sql = "select v.raceId,(s.startTime-v.starttime_avg) as startTime_dev,s.startTime,v.starttime_avg                from raceresult s,racemanagement m,                     (select raceId,avg(startTime) as starttime_avg from raceresult                      where startTime between 0 and 9.9                      group by raceId                      having count(*) = 6 ) v                where s.raceId = v.raceId                  and s.raceId = m.raceId                  and s.toban = '%s'                  and m.raceDate < '%s'                  order by raceId desc                  limit 30 "               % (toban,raceDate)
    cursor.execute(sel_sql)
    startInfoList=cursor.fetchall()
print(len(startInfoList))
print(startInfoList)


# In[15]:


# 他の人よりどれだけスタートが早いと、進入コース別に、結果（1着、2着、3着、それ以下）にどれだけ影響があるのか。
# 進入コースとスタート偏差にはどれだけ関係があるのか。アウトになるほどばらつきが大きくなる？
# 


# In[ ]:





# In[16]:


# メモリ使用チェック
print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
print(" ------------------------------------ ")
for var_name in dir():
    if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 1000: #ここだけアレンジ
        print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))


# In[ ]:




