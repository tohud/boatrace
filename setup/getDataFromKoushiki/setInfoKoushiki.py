#!/usr/bin/env python
# coding: utf-8

# In[3]:


#
import json
import re
import unicodedata

import pymysql
import getInfoKoushiki


# In[ ]:


def setRaceManagementKoushiki(dbh,raceDate):
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
    

