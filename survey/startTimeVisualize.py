#!/usr/bin/env python
# coding: utf-8

# In[19]:


# ToDo 

# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm


# In[20]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[21]:


# 分析期間の指定は一旦ここでまとめてみる。
analyzeStartDate="20180101"
analyzeEndDate="20180131"


# In[22]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[23]:


# 日付と登録番号を与えて、該当選手の直近30回のスタート時刻の、各レース平均に対する偏差平均を出す。フライング除く。
# 現在は、各レース平均に対する偏差のリストを返している。
raceDate = analyzeEndDate
toban="4337"
with dbh.cursor() as cursor:
    sel_sql = "select v.raceId,(s.startTime-v.starttime_avg) as startTime_dev,s.startTime,v.starttime_avg                from raceresult s,racemanagement m,                     (select raceId,avg(startTime) as starttime_avg from raceresult                      where startTime between 0 and 9.9                      group by raceId                      having count(*) = 6 ) v                where s.raceId = v.raceId                  and s.raceId = m.raceId                  and s.toban = '%s'                  and m.raceDate < '%s'                  order by raceId desc                  limit 30 "               % (toban,raceDate)
    cursor.execute(sel_sql)
    startInfoList=cursor.fetchall()
print(len(startInfoList))
#print(startInfoList)


# In[24]:


# 他の人よりどれだけスタートが早いと、進入コース別に、結果（1着、2着、3着、それ以下）にどれだけ影響があるのか。


# In[25]:


# 進入コースとスタート偏差にはどれだけ関係があるのか。アウトになるほどばらつきが大きくなる？
with dbh.cursor() as cursor:
    sel_sql = "select v.raceId,(s.startTime-v.starttime_avg) as startTime_dev,s.startLane,s.goalRank,s.lane                from raceresult s, racemanagement m,                     (select raceId,avg(startTime) as starttime_avg from raceresult                      where startTime between 0 and 9.9                      group by raceId                      having count(*) = 6 ) v                where s.raceId = v.raceId                  and s.raceId = m.raceId                  and m.raceDate between '%s' and '%s' "               % (analyzeStartDate,analyzeEndDate)
    cursor.execute(sel_sql)
    startInfoList=cursor.fetchall()
print(len(startInfoList))
#print(startInfoList)


# In[26]:


df = pd.io.json.json_normalize(startInfoList)
df.head()


# In[28]:


# まずは素朴に順位別にstartTime_devを見てみる。
# 着順別の傾向。明らかに、ゴールした順位とスタートタイムは影響する。0.01秒でも十分な違いと見て良さそう。
groupeddf=df.groupby('goalRank')
groupeddf.describe()


# In[29]:


# 上記をグラフ化。グラフにするとあまり見えない。
#df[['goalRank','startTime_dev']].plot(kind='scatter',x='goalRank',y='startTime_dev')


# In[30]:


# まずは素朴に順位別にstartTime_devを見てみる。
# 進入コース別の傾向。平均で、1レーンからスタートが早く、順に6レーンは遅い傾向がある。インの方が合わせやすいということか。
# しかし標準偏差ははっきりしない。外側だとぶれやすいわけではない。
groupeddf=df.groupby('startLane')
groupeddf.describe()


# In[13]:


# まずは素朴に順位別にstartTime_devを見てみる。
# 枠別の傾向。進入コース別と同じ傾向。枠と進入コースがほぼ同等？なので、当然といえば当然。
# ToDo 枠と進入コースの関係を表示する
groupeddf=df.groupby('lane')
groupeddf.describe()


# In[14]:


# 枠と進入コースがどれだけ一致するかをチェックする。


# In[15]:


# 過去のstartTime_devから未来は予測できるのか？自己相関があるか、どのくらいの期間影響するのか、を検証。
# 30レース以上に出場している選手に限定する ←データが集まってないのでいったん、20レースにする。
with dbh.cursor() as cursor:
    sel_sql = "select (s.startTime-v.starttime_avg) as startTime_dev,s.toban                from raceresult s,racemanagement m,                     (select toban from raceresult                      where startTime between 0 and 9.9                      group by toban having count(*) > 20) t,                    (select raceId,avg(startTime) as starttime_avg from raceresult                      where startTime between 0 and 9.9                      group by raceId                      having count(*) = 6 ) v                where s.raceId = v.raceId                  and s.toban  = t.toban                  and s.raceId = m.raceId                  and m.raceDate between '%s' and '%s'                order by s.toban,s.raceId desc"               % (analyzeStartDate,analyzeEndDate)
    cursor.execute(sel_sql)
    startInfoList=cursor.fetchall()
print(len(startInfoList))
#print(startInfoList)
df = pd.io.json.json_normalize(startInfoList)
df.head()


# In[16]:


groupeddf=df.groupby('toban')
groupeddf.head()


# In[17]:


df[df['toban']=='4873'].head()
# todo 次に、自己相関を見てみる。


# In[18]:


# メモリ使用チェック
print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
print(" ------------------------------------ ")
for var_name in dir():
    if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 1000: #ここだけアレンジ
        print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))


# In[ ]:





# In[ ]:





# In[ ]:




