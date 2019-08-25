#!/usr/bin/env python
# coding: utf-8

# In[49]:


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
import csv
from itertools import chain

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import scipy.stats

import matplotlib.pyplot as plt
from statistics import mean


# In[50]:


# keras用ライブラリ
from keras.datasets import mnist
from keras.models import Sequential, model_from_json,load_model
from keras.layers import Dense, Activation
from keras.optimizers import SGD
from keras.utils import np_utils

# LGBM用ライブラリ
import lightgbm as lgb


# In[51]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[52]:


# 舟券の配列を取得
funakenList=[]
with open(os.environ['BR_HOME']+'/boatrace/config/3t_list.dat') as f:
    reader=csv.reader(f)
    for row in reader:
        funakenList.append(row)
funakenID = [i for i in range(120)]
funakenDict=dict(zip(funakenList[0],funakenID))


# In[53]:


# 分析期間の指定は一旦ここでまとめてみる。
simStartDate="20190101"
simEndDate="20190331"


# In[54]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[55]:


# データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_rentai_v                where raceDate between '%s' and '%s'                order by raceId "               % (simStartDate,simEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("simdata:",len(loadList))


# In[56]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[57]:


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


# In[58]:


# validation向けに平均値、標準偏差を出しておく
zscore_param=xdf.describe()
# 変換の方法はこちら。
print( (xdf.loc["0":"1",["l1boat2r"] ]-zscore_param['l1boat2r']['mean'])/zscore_param['l1boat2r']['std'] )


# In[59]:


# normalizeしておく
# ★validationの時に要注意。
# LGBMではxdf、kerasではxdf_nを使う。
xdf_n=xdf.apply(scipy.stats.zscore, axis=0)


# In[60]:


xdf_n.head()


# In[61]:


# ファイルから作った辞書で変換する
ydf=df['funaken']
ydf=pd.DataFrame(ydf.replace(funakenDict))
ydf['funaken']=ydf['funaken'].astype(int)
#ydf.head()

# ydfはone-hotにしておく。
y_onehot=np.eye(120)[ydf['funaken']]
print(y_onehot)


# In[62]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
raceId_df=df['raceId'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
print(odf)
print(raceId_df)


# In[63]:


# keras_perseptronをloadしてシミュレート

model_path=os.path.join(os.environ['BR_HOME'],"boatrace/models")
kp_model_modelfile=os.path.join(model_path,'keras_perceptron_model.json')
kp_model_weightfile=os.path.join(model_path,'keras_perceptron_weight.json')

with open(kp_model_modelfile,"r") as kp_modelf:
    tmp_model_json = ""
    for line in kp_modelf:
        tmp_model_json+=line

kp_model=model_from_json(tmp_model_json)
kp_model.load_weights(kp_model_weightfile)

kp_PredictList=kp_model.predict(xdf,batch_size=len(xdf))


# In[64]:


# LGBMをloadしてシミュレート

lg_model_modelfile=os.path.join(model_path,'20190714063621.txt')
lg_model=lgb.Booster(model_file=lg_model_modelfile )

lg_y_pred = lg_model.predict(xdf, num_iteration=lg_model.best_iteration)


# In[65]:


print(kp_PredictList[0])
print(lg_y_pred[0])


# In[66]:


emsembleList=[]
for i in range(len(kp_PredictList) ):
#    emsembleList.append([ scipy.stats.hmean([kp_PredictList[i][j],lg_y_pred[i][j]] ) for j in range(120) ])
    emsembleList.append([ sum([kp_PredictList[i][j],lg_y_pred[i][j]] )/2. for j in range(120) ])
#print(emsembleList)


# In[67]:


print(sum(emsembleList[100]))


# In[72]:



resAmount=0
buyAmount=0
resCnt=0
buyCnt=0

predicts=[]
returns =[]

for i in range(len(raceId_df) ):
    raceId=raceId_df[i]
    with dbh.cursor() as cursor:
        sel_sql = "select funaken,odds from raceodds                    where oddsType = '3t'                    and raceId = '%s'                    order by funaken"                    % (raceId)

        cursor.execute(sel_sql)
        loadList=pd.DataFrame(cursor.fetchall())
        loadList=pd.DataFrame(loadList.replace(funakenDict))
                
    for j in range(120):
        #if emsembleList[i][j]> 0.05 and ( (emsembleList[i][j] * (loadList[loadList['funaken']==j]['odds'])).values[0] > 1.5) :
        if emsembleList[i][j]> 0.10 and ( (emsembleList[i][j] * (loadList[loadList['funaken']==j]['odds'])).values[0] > 0.5) :
            print("buy:",raceId,i,j,loadList[loadList['funaken']==j]['odds'].values[0],round(emsembleList[i][j],3) )
            #predicts.append([ loadList[loadList['funaken']==j]['odds'].values[0],round(emsembleList[i][j],3)] )
            predicts.append(loadList[loadList['funaken']==j]['odds'].values[0])
            buyAmount+=1
            buyCnt+=1
            if list(y_onehot[i]).index(1)==j:
            #if ydf[i]==j:
                print("☆hit!☆:",raceId,j,loadList[loadList['funaken']==j]['odds'].values[0])
                returns.append(odf[i])
                resAmount += odf[i]
                resCnt+=1
            else:
                pass
#res=net.model.predict_on_batch(xdf[1:3])


# In[73]:


print("resultReturn:",resAmount/buyAmount)
print("totalRace,buy,return",len(ydf),buyAmount,resAmount )
print("rate:",resCnt/buyCnt)


# In[74]:


plt.plot(predicts)
plt.plot(returns)


# In[78]:


plt.hist(predicts, bins=41,range=(0,40))
plt.hist(returns)
plt.show()


# In[ ]:




