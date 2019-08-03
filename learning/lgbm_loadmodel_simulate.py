#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 保存されたモデルをロードして別の期間でのシミュレートをする


# In[2]:


# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm
import math
import tensorflow as tf
import collections
from datetime import datetime

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import csv
from itertools import chain


# In[3]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler

# model保存パスのセット
model_path=os.path.join(os.environ['BR_HOME'],"boatrace/models")


# In[4]:


# 舟券の配列を取得
funakenList=[]
with open(os.environ['BR_HOME']+'/boatrace/config/3t_list.dat') as f:
    reader=csv.reader(f)
    for row in reader:
        funakenList.append(row)
funakenID = [i for i in range(120)]
funakenDict=dict(zip(funakenList[0],funakenID))


# In[16]:


# 分析期間の指定は一旦ここでまとめてみる。
simStartDate="20190101"
simEndDate="20190531"

model_name="20190714063621.txt"


# In[8]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[10]:


# データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_rentai_v                where raceDate between '%s' and '%s'                order by raceId "               % (simStartDate,simEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("simdata:",len(loadList))


# In[11]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[12]:


# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
# オッズから作ったスコアは効きすぎるので捨ててみる
xdf=xdf.drop(['l1score','l2score','l3score','l4score','l5score','l6score'],axis=1)
#xdf=xdf.drop(['l1Fcnt','l2Fcnt','l3Fcnt','l4Fcnt','l5Fcnt','l6Fcnt'],axis=1)
#xdf=xdf.drop(['l1oldavgstdev','l2oldavgstdev','l3oldavgstdev','l4oldavgstdev','l5oldavgstdev','l6oldavgstdev'],axis=1)

rankLabel=LabelEncoder()
rankLabel=rankLabel.fit(xdf['l1rank'])
xdf['l1rank']=rankLabel.transform(xdf['l1rank'])
xdf['l2rank']=rankLabel.transform(xdf['l2rank'])
xdf['l3rank']=rankLabel.transform(xdf['l3rank'])
xdf['l4rank']=rankLabel.transform(xdf['l4rank'])
xdf['l5rank']=rankLabel.transform(xdf['l5rank'])
xdf['l6rank']=rankLabel.transform(xdf['l6rank'])
xdf.head()


# In[13]:


xdf.describe()


# In[14]:


# ファイルから作った辞書で変換する
ydf=df['funaken']
ydf=pd.DataFrame(ydf.replace(funakenDict))
ydf['funaken']=ydf['funaken'].astype(int)
#print(ydf.head())
print(ydf['funaken'].dtype)


# In[15]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
#print(odf)


# In[18]:


model=lgb.Booster(model_file=os.path.join(model_path,model_name) )


# In[20]:


y_pred = model.predict(xdf, num_iteration=model.best_iteration)
y_pred_max = np.argmax(y_pred, axis=1)  # 最尤と判断したクラスの値にする

# 精度 (Accuracy) を計算する
accuracy = sum(ydf['funaken'] == y_pred_max) / len(ydf)
print("accuracy:",accuracy)

# 回収率を計算
res=0
for i in range(len(ydf)):
    if (ydf.iloc[i])['funaken']==y_pred_max[i]:
        #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
        res += odf[i] -1
    else:
        #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
        pass
print("resultReturn:",res/len(ydf))


# In[21]:


# オッズを見て判断する場合
resAmount=0
buyAmount=0

dfIndexList=ydf['funaken'].index
for i in range(len(ydf)):
    raceId = df.iloc[dfIndexList[i]]['raceId']
    #print(raceId)
    with dbh.cursor() as cursor:
        sel_sql = "select funaken,odds from raceodds                    where oddsType = '3t'                    and raceId = '%s'                    order by funaken"                    % (raceId)
        cursor.execute(sel_sql)
        loadList=pd.DataFrame(cursor.fetchall())
        loadList=pd.DataFrame(loadList.replace(funakenDict))
    for j in range(120):
        # y_predの閾値を下げてみる。
        if y_pred[i][j]> 0.05 and ( (y_pred[i][j] * (loadList[loadList['funaken']==j]['odds'])).values[0] > 1.5) :
            print("buy:",raceId,i,j,loadList[loadList['funaken']==j]['odds'].values[0],round(y_pred[i][j],3) )
            buyAmount+=1
            if ydf['funaken'].iloc[i]==j:
                print("☆hit!☆:",raceId,j,loadList[loadList['funaken']==j]['odds'].values[0])
                resAmount += odf[i]
            else:
                pass


# In[22]:


print("resultReturn:",resAmount/buyAmount)
print("totalRace,buy,return",len(ydf),buyAmount,resAmount )


# In[ ]:




