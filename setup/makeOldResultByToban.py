#!/usr/bin/env python
# coding: utf-8

# In[33]:


# レースID・登録番号ごとに、直近100レース分の順位分布と平均スタートタイム偏差を取得し、
# バッチでテーブルにinsertする。

# 汎用ライブラリのimport
import sys
import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import math
import csv


# In[34]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[35]:


args = sys.argv
if len(args)==0:
    Debug=True
else:
    Debug=False
    
# 分析期間の指定は一旦ここでまとめてみる。
if Debug:
    trainStartDate="20170919"
    trainEndDate="20170919"
else:
    trainStartDate=args[1]
    trainEndDate=args[2]


# In[36]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[37]:


# 指定期間のレースIDリストを作る
with dbh.cursor() as cursor:
    sel_sql = "select raceId from racemanagement                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
print("raceIdList:",len(raceIdList))


# In[ ]:





# In[38]:


for raceId in [ raceIdList[i]['raceId'] for i in range(len(raceIdList))]:
    print(raceId)
    # 各レースIDで、メンバーリストを順次とっていく
    with dbh.cursor() as membercursor:
        selmember_sql = "select rmToban from racemember                          where raceId = '%s' order by rmLane"                          % (raceId)
        membercursor.execute(selmember_sql)
        tmpMemList=membercursor.fetchall()
        # 取得したメンバーリストに基づき、それぞれの過去レースリストを取得
        with dbh.cursor() as oldResultCursor:
            #tmpOldDict={'raceId':racdId}
            lane=0
            for tobanHash in tmpMemList:
                lane+=1
                # あとでまた変換するのが面倒だから、変数名をレーン別にわける。
                sel_sql = "select                                count(CASE WHEN a.goalRank=1 THEN a.goalRank END)/100 as oldRank1,                               count(CASE WHEN a.goalRank=2 THEN a.goalRank END)/100 as oldRank2,                               count(CASE WHEN a.goalRank=3 THEN a.goalRank END)/100 as oldRank3,                               count(CASE WHEN a.goalRank=4 THEN a.goalRank END)/100 as oldRank4,                               count(CASE WHEN a.goalRank=5 THEN a.goalRank END)/100 as oldRank5,                               count(CASE WHEN a.goalRank=6 THEN a.goalRank END)/100 as oldRank6                            from (                                 select tr.goalRank from raceresult tr                                where tr.toban = '%s'                                 and tr.raceId < '%s'                                order by tr.raceId desc                                 limit 100                            ) a "                           % (tobanHash['rmToban'],raceId)
                oldResultCursor.execute(sel_sql)
                tmpOldDict=(oldResultCursor.fetchall())[0]
                
                # 次に、過去のレースタイム関連情報をとってくる。
                seltime_sql = "select                                  rr.toban,avg(rr.startDev) as avgStartDev,avg(rr.startTime) as avgStartTime                                from                                 (   select                                         r.raceId,r.toban,                                         ( r.startTime-avgAll.avgStartAll) as startDev,                                         r.startTime                                     from                                         raceresult r,                                        ( select raceId,avg(startTime) as avgStartAll from raceresult                                           group by raceId ) avgAll                                      where avgAll.raceId = r.raceId                                       and r.toban = '%s'                                       and r.raceId < '%s'                                     group by r.raceId,r.toban,r.startTime                                     order by r.raceId desc                                     limit 100  ) as rr                                group by rr.toban "                               % (tobanHash['rmToban'],raceId)
                
                oldResultCursor.execute(seltime_sql)
                try:
                    tmpOldTimeDict=(oldResultCursor.fetchall())[0]
                except IndexError as e:
                    tmpOldTimeDict={'avgStartDev':0.0,'avgStartTime':0.20}
                
        # 終わったらraceId別にテーブルに突っ込む
                with dbh.cursor() as insOldRaceByTobanCursor:
                    ins_sql = "INSERT INTO oldResultByToban                                (raceId,toban,lane,oldRank1,oldRank2,oldRank3,oldRank4,oldRank5,oldRank6,                                 avgStartDev,avgStartTime)                                VALUES                                ('%s','%s',%d,%f,%f,%f,%f,%f,%f,%f,%f) "                              % (raceId,tobanHash['rmToban'],lane,
                                 tmpOldDict['oldRank1'],tmpOldDict['oldRank2'],tmpOldDict['oldRank3'],
                                 tmpOldDict['oldRank4'],tmpOldDict['oldRank5'],tmpOldDict['oldRank6'],
                                 tmpOldTimeDict['avgStartDev']  ,tmpOldTimeDict['avgStartTime']
                                )
                    #print(ins_sql)
                    insOldRaceByTobanCursor.execute(ins_sql)
                    dbh.commit()


# In[ ]:




