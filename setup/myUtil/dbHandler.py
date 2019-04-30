#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import json
import pymysql


# In[5]:


def getDBHandle():
    with open(os.environ['BR_HOME']+'/config_nogit/mysqlUser.json') as mysqlconfig:
        mysqlConfig=json.load(mysqlconfig)

    dbh=pymysql.connect(
        host='localhost',
        user=mysqlConfig['user'],
        password=mysqlConfig['password'],
        db='boatrace',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

    return dbh


# In[6]:


def closeDBHandle(dbh):
    dbh.close()


# In[ ]:




