#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from bs4 import BeautifulSoup
import json
import urllib.request as u
import time
import re
import sys

import unicodedata


# In[2]:


# レース一覧の取得
def getRaceManagementKoushiki(ymd):
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/index?hd=%s" % ymd)
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    for block in soup.select(".table1"):
        recs=block.select("tr")
        for rec in recs:
            tds=rec.select("td")
            if len(tds)>0:
                tmp=tds[0]
                #placePattern=r'tpl=(\d\d)'
                placePattern=r'tv(\d*)'
                placeId=re.search(placePattern,str(tmp)).group(1)
                #print(placeId)
                
                tmp=tds[2]
                gradePattern=r'class=\"is-(.*?)\"'
                grade=re.search(gradePattern,str(tmp)).group(1)
                #print(grade)
                
                rname=tds[4].string
                #print(rname)
                
                for i in range(1,12+1):
                    raceId=ymd+'-'+str(placeId).zfill(2)+'-'+str(i).zfill(2)
                    raceDate=ymd
                    raceNumber=i
                    raceName=rname
                    raceGrade=grade
                    racePlaceId=str(placeId).zfill(2)
                    
                    yield raceId,raceDate,raceNumber,raceName,raceGrade,racePlaceId


# In[3]:


# レース直前情報の取得（天候）
def getRaceBeforeInfoWeatherKoushiki(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/beforeinfo?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    try:
        soup = (BeautifulSoup(html,"html.parser").select(".weather1_body")[0])
    
        direction=(soup.select(".is-direction"))[0]
        direction=((direction.select("p"))[0].get("class"))[1]
        #print("direction:"+direction)
    
        weather=(soup.select(".is-weather"))[0]
        weather=(weather.select(".weather1_bodyUnitLabelTitle"))[0].string
        #print("weather:"+str(weather) )
        weather=unicodedata.normalize('NFKC', weather)
    
        temperature=(soup.select(".is-direction"))[0]
        temperature=((temperature.select(".weather1_bodyUnitLabel"))[0].select(".weather1_bodyUnitLabelData"))[0].string
        temperature=temperature.strip('℃')
        #print("temperature:"+temperature)
    
        wind_speed=(soup.select(".is-wind"))[0]
        wind_speed=(wind_speed.select(".weather1_bodyUnitLabelData"))[0].string
        wind_speed=wind_speed.strip("m")
        #print(wind_speed)
    
        wind_direction=(soup.select(".is-windDirection"))[0]
        wind_direction=((wind_direction.select("p"))[0].get("class"))[1]
        #print(wind_direction)
    
        water_temperature=(soup.select(".is-waterTemperature"))[0]
        water_temperature=water_temperature.select(".weather1_bodyUnitLabelData")[0].string
        water_temperature=water_temperature.strip("℃")
        #print(water_temperature)

        wave=(soup.select(".is-wave"))[0]
        wave=wave.select(".weather1_bodyUnitLabelData")[0].string
        wave=wave.strip("cm")
        #print(wave)
        
        yield temperature,weather,wind_speed,water_temperature,wave

    except IndexError as e:
        print('[SKIP]IndexError発生 at 直前情報　天候取得　raceId:'+raceId )
    


# In[4]:


def getRaceMemberKoushiki(raceId):
    #html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/index?hd=%s" % ymd)
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/racelist?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    for block in soup.select(".is-fs12"):
        #print(block)
        recs=block.select("tr")
        rec=recs[0]
        tds=rec.select("td")
        lane=unicodedata.normalize('NFKC', tds[0].string)        
        tobanId=((tds[2].select(".is-fs11"))[0].contents[0].strip())[0:4]
        rank=(tds[2].select("span"))[0].string
        #print("lane:",lane)
        #print("tobanId:",tobanId)
        #print("rank:",rank)
        #print(tds[2]) ※　他に取りたい項目があればここからとってくる
        
        yield lane,tobanId,rank


# In[5]:


def getOldOddsKoushiki3rentan(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    #print(raceDate,raceNumber,placeId)
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/odds3t?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    
    # 3連単の組み合わせリストを辞書順に作成
    sanrentanList=[]
    for i in range(1,6+1):
        for j in range(1,6+1):
            for k in range(1,6+1):
                if (i==j or i==k or j==k):
                    continue
                else:
                    sanrentanList.append(str(i)+"-"+str(j)+"-"+str(k))
    sorted(sanrentanList)
    
    sanrentanOddsList=[]
    for oddspoint in soup.select(".oddsPoint"):
        sanrentanOddsList.append(oddspoint.string)
    
    cnt=0
    try:
        for i in range(6):
            for j in range(20):
                yield sanrentanList[i*20+j],sanrentanOddsList[i+j*6]
    except IndexError as e:
        print('[SKIP]IndexError発生 at 3連単オッズ取得　raceId:'+raceId )


# In[6]:


def getOldOddsKoushiki3renfuku(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/odds3f?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    
    # 3連複の組み合わせリストをサイトからの取得可能順に作成
    sanrenfukuList=[]
    for k in range(3,6+1):
        sanrenfukuList.append(str(1)+"-"+str(2)+"-"+str(k))
    for k in range(4,6+1):
        for i in range(1,2+1):
            sanrenfukuList.append(str(i)+"-"+str(3)+"-"+str(k))
    for k in range(5,6+1):
        for i in range(1,3+1):
            sanrenfukuList.append(str(i)+"-"+str(4)+"-"+str(k))
    for i in range(1,4+1):
        sanrenfukuList.append(str(i)+"-"+str(5)+"-"+str(6))
    
    #print(sanrenfukuList)
    sanrenfukuOddsList=[]
    for oddspoint in soup.select(".oddsPoint"):
        sanrenfukuOddsList.append(oddspoint.string)
    
    try:
        for i in range(len(sanrenfukuList)):
            yield sanrenfukuList[i],sanrenfukuOddsList[i]
    except IndexError as e:
        print('[SKIP]IndexError発生 at 3連複オッズ取得 raceId:'+raceId)
    


# In[7]:


def getOldOddsKoushiki2rentan(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/odds2tf?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    
    try:
        block =(soup.select(".is-p3-0"))[0]
        tmpcnt1=1
        for trs in block.select("tr"):
            tmpcnt2=0
            tmp1stlane=1
            for tds in trs.select("td"):
                if tmpcnt2%2==0:
                    cs=tds.string
                else:
                    odds=tds.string
                    yield str(tmp1stlane)+"-"+str(cs),odds
                    tmp1stlane+=1
                tmpcnt2+=1
            tmpcnt1+=1
    except IndexError as e:
        print('[SKIP]IndexError発生 at 2連単オッズ取得 raceId:'+raceId)


# In[8]:


def getOldOddsKoushiki2renfuku(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    print(raceDate,raceNumber,placeId)
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/odds2tf?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    
    try:
        block =(soup.select(".is-p3-0"))[1]
        tmpcnt1=1
        for trs in block.select("tr"):
            tmpcnt2=0
            tmp1stlane=1
            for tds in trs.select("td"):
                if tmpcnt2%2==0:
                    cs=tds.string
                elif tds['class'][0] == "oddsPoint":
                    odds=tds.string
                    yield str(tmp1stlane)+"-"+str(cs),odds
                    tmp1stlane+=1
                tmpcnt2+=1
            tmpcnt1+=1
    except IndexError as e:
        print('[SKIP]IndexError発生 at 2連複オッズ取得　raceId:'+raceId)


# In[9]:


def getOldOddsKoushikiTansho(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    #print(raceDate,raceNumber,placeId)
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/oddstf?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")
    
    try:
        block =((soup.select(".grid_unit"))[0].select("table")[0]).select(".oddsPoint")
        i=1
        for tds in block:
            yield i,tds.string
            i+=1
    except IndexError as e:
        print('[SKIP]IndexError発生 at 単勝オッズ取得　raceId:'+raceId )


# In[ ]:


def getOldOddsKoushikiResult(raceId):
    raceDate=raceId[0:8]
    raceNumber=int(raceId[12:14])
    placeId=raceId[9:11]
    #print(raceDate,raceNumber,placeId)
    html = u.urlopen("https://www.boatrace.jp/owpc/pc/race/raceresult?rno=%d&jcd=%s&hd=%s" %(raceNumber,placeId,raceDate) )
    time.sleep(1)
    soup = BeautifulSoup(html,"html.parser")

    try:
        blocks_time =(soup.select(".is-w495"))[0].select("tr")
        blocks_start =(soup.select(".is-w495"))[1].select("tr")
        #print(blocks_start)
        del blocks_time[0] # 1行目のヘッダは削除
        del blocks_start[0] # 1行目のヘッダは削除

        tds_start=[]
        for block_start in blocks_start:
            tmp_starttime=((block_start.select(".table1_boatImage1TimeInner"))[0].string.split(' '))[0]
            if tmp_starttime[0]=='F':
                tmp_starttime='-0'+tmp_starttime[1:]
            else:
                tmp_starttime='0'+tmp_starttime
            tds_start.append(tmp_starttime.strip())
            
        for i in range(6):
            block_time=blocks_time[i]
            tds_time = block_time.select("td")
            goalRank=i+1
            lane=int(tds_time[1].string)
            toban=(tds_time[2].select(".is-fs12"))[0].string
            startTime=float(tds_start[int(tds_time[1].string)-1])
            # 1'51"2 のようなレースタイム表記をFLOATに変換。空白の場合はinfにする
            if len(tds_time[3].string.strip())  > 0:
                gl_m,gl_s,gl_ms = re.split('[\'\"]',tds_time[3].string.strip())
                goalTime=int(gl_m)*60+int(gl_s)+int(gl_ms)/10.0
            else:
                goalTime=999.9
            #print(block)
            yield goalRank,lane,toban,startTime,goalTime
    except IndexError as e:
        print('[SKIP]IndexError発生 at 結果取得 raceid:'+raceId)
    

