#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 公式からとってくる。
# レースリスト、レースの参加メンバー、直前のオッズリストをESに突っ込む
# https://www.boatrace.jp/owpc/pc/race/index?hd=%s
# http://odds.kyotei24.jp/
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
#from getDataFromKoushiki import setInfoKoushiki
from myUtil import dbHandler


# In[41]:


print(os.environ['GACRP_HOME'])
print(os.environ['BR_HOME'])


# In[42]:


dbh=dbHandler.getDBHandle()


# In[43]:


#dbHandler.closeDBHandle(dbh)


# In[44]:


#　会場とplaceIdとの紐づけファイルをロード。たぶん使わない。
with open('../config/def-place.json','r',encoding='utf8') as defPlace:
    placeDict=json.load(defPlace)
print(placeDict[0]['placeId'],placeDict[0]['placeName'])
#for i in range(len(placeDict)):
#    print("|"+placeDict[i]['placeId']+"|"+placeDict[i]['placeName']+"|")


# In[45]:


raceDate="20190322"


# In[ ]:





# In[46]:


# レースの一覧を取得し、足りないracemanegementを作る。

with dbh.cursor() as cursor:
    for ret in getInfoKoushiki.getRaceManagementKoushiki(raceDate):
        #racemanagementをここでは整備する。
        sel_sql="SELECT count(*) FROM racemanagement WHERE raceid='%s'" % (ret[0])
        cursor.execute(sel_sql)
        results=cursor.fetchone()
        
        if results['count(*)']== 0: #なければINSERT
            ins_sql="INSERT INTO racemanagement (raceId,raceDate,raceNumber,raceGrade,racePlaceId,racebeforeinfo_flg,racemember_flg,raceodds3t_flg,raceodds3f_flg,raceodds2t_flg,raceodds2f_flg,raceodds1t_flg,raceodds1f_flg,raceresult_flg) VALUES ('%s' ,'%s',%d,'%s','%s',FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)" % (ret[0],ret[1],ret[2],ret[4],ret[5])
            #print(ins_sql)
            cursor.execute(ins_sql)
    dbh.commit()


# In[47]:


# racemanegementをもとに、レースの直前情報を取得する。
# ただし、beforeinfoはレースで一意の情報（Weather）と、メンバーごとの情報をわける。
dbh.rollback()
with dbh.cursor() as cursor:
    #racemanagementで、racememberが未取得になっていたら取得してフラグをtrueにする。
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and racebeforeinfo_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)        
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getRaceBeforeInfoWeatherKoushiki(raceId):
                print(ret)
                ins_sql="INSERT INTO racebeforeinfo (raceId,raceTemperature,raceWeather,raceWindSpeed,raceSurfaceTemperature,raceWaveHeight) VALUES ('%s' ,%f,'%s','%f','%f','%d')" % (raceId,float(ret[0]),ret[1],float(ret[2]),float(ret[3]),int(ret[4]) )
                #print(ins_sql)
                ins_cursor.execute(ins_sql)
            upd_sql="UPDATE racemanagement SET racebeforeinfo_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()


# In[48]:


dbh.rollback()
with dbh.cursor() as cursor:
    #racemanagementで、racememberが未取得になっていたら取得してフラグをtrueにする。
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and racemember_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getRaceMemberKoushiki(raceId):
                #print(ret)
                ins_sql="INSERT INTO racemember (raceId,rmLane,rmToban,rmRank) VALUES ('%s' ,%d,'%s','%s')" % (raceId,int(ret[0]),ret[1],ret[2])
                #print(ins_sql)
                ins_cursor.execute(ins_sql)
            upd_sql="UPDATE racemanagement SET racemember_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()


# In[ ]:





# In[49]:



dbh.rollback()

with dbh.cursor() as cursor:
 #racemanagementで3連単のオッズを埋める
 sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and raceodds3t_flg = FALSE" % (raceDate)
 cursor.execute(sel_sql)
 raceIdList=cursor.fetchall()
 for raceIdhash in raceIdList:
     raceId = raceIdhash['raceId']
     print(raceId)
     with dbh.cursor() as ins_cursor:
         for ret in getInfoKoushiki.getOldOddsKoushiki3rentan(raceId):
             #print(ret)
             if ret[1] == '欠場':
                 print('[SKIP]欠場 at 3連単オッズ取得 raceId:'+raceId)
             else:
                 ins_sql="INSERT INTO raceodds (raceId,oddsType,funaken,odds) VALUES ('%s' ,'3t','%s','%s')" % (raceId,ret[0],ret[1])
                 ins_cursor.execute(ins_sql)
         upd_sql = "UPDATE racemanagement SET raceodds3t_flg = TRUE where raceId ='%s'" % (raceId)
         ins_cursor.execute(upd_sql)
         dbh.commit()


# In[50]:



#raceId="20190321-01-01"
dbh.rollback()

with dbh.cursor() as cursor:
    #racemanagementで3連複のオッズを埋める
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and raceodds3f_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getOldOddsKoushiki3renfuku(raceId):
                #print(ret)
                if ret[1] == '欠場':
                    print('[SKIP]欠場 at 3連複オッズ取得 raceId:'+raceId)
                else:
                    ins_sql="INSERT INTO raceodds (raceId,oddsType,funaken,odds) VALUES ('%s' ,'3f','%s','%s')" % (raceId,ret[0],ret[1])
                    ins_cursor.execute(ins_sql)
            upd_sql = "UPDATE racemanagement SET raceodds3f_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()


# In[51]:


#raceId="20190321-01-01"
dbh.rollback()

with dbh.cursor() as cursor:
    #racemanagementで2連単のオッズを埋める
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and raceodds2t_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getOldOddsKoushiki2rentan(raceId):
                #print(ret)
                if ret[1] == '欠場':
                    print('[SKIP]欠場 at 2連単オッズ取得 raceId:'+raceId)
                else:
                    ins_sql="INSERT INTO raceodds (raceId,oddsType,funaken,odds) VALUES ('%s' ,'2t','%s','%s')" % (raceId,ret[0],ret[1])
                    ins_cursor.execute(ins_sql)
            upd_sql = "UPDATE racemanagement SET raceodds2t_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()
    


# In[52]:


#raceId="20190321-01-01"
#for ret in getOldOddsKoushiki2renfuku(raceId):
#    print(ret)

dbh.rollback()

with dbh.cursor() as cursor:
    #racemanagementで2連複のオッズを埋める
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and raceodds2f_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getOldOddsKoushiki2renfuku(raceId):
                #print(ret)
                if ret[1] == '欠場':
                    print('[SKIP]欠場 at 2連複オッズ取得 raceId:'+raceId)
                else:
                    ins_sql="INSERT INTO raceodds (raceId,oddsType,funaken,odds) VALUES ('%s' ,'2f','%s','%s')" % (raceId,ret[0],ret[1])
                    ins_cursor.execute(ins_sql)
            upd_sql = "UPDATE racemanagement SET raceodds2f_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()


# In[53]:


#raceId="20190321-01-01"
#for ret in getOldOddsKoushikiTansho(raceId):
#    print(ret)

dbh.rollback()

with dbh.cursor() as cursor:
    #racemanagementで単勝のオッズを埋める
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and raceodds1t_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getOldOddsKoushikiTansho(raceId):
                #print(ret)
                if ret[1] == '欠場':
                    print('[SKIP]欠場 at 単勝オッズ取得 raceId:'+raceId)
                else:
                    ins_sql="INSERT INTO raceodds (raceId,oddsType,funaken,odds) VALUES ('%s' ,'1t','%s','%s')" % (raceId,ret[0],ret[1])
                    ins_cursor.execute(ins_sql)
            upd_sql = "UPDATE racemanagement SET raceodds1t_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()

            


# In[ ]:





# In[54]:


dbh.rollback()

with dbh.cursor() as cursor:
    sel_sql = "SELECT raceId FROM racemanagement WHERE raceDate='%s' and raceresult_flg = FALSE" % (raceDate)
    cursor.execute(sel_sql)
    raceIdList=cursor.fetchall()
    for raceIdhash in raceIdList:
        raceId = raceIdhash['raceId']
        print(raceId)
        with dbh.cursor() as ins_cursor:
            for ret in getInfoKoushiki.getOldOddsKoushikiResult(raceId):
                ins_sql="INSERT INTO raceresult (raceId,goalRank,lane,toban,startTime,goalTime) VALUES ('%s' ,%d, %d, '%s',%f,%f)" % (raceId,ret[0],ret[1],ret[2],ret[3],ret[4])
                ins_cursor.execute(ins_sql)
            upd_sql = "UPDATE racemanagement SET raceresult_flg = TRUE where raceId ='%s'" % (raceId)
            ins_cursor.execute(upd_sql)
            dbh.commit()


# In[ ]:




