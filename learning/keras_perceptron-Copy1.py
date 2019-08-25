#!/usr/bin/env python
# coding: utf-8

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
import csv
from itertools import chain

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import scipy.stats


# In[3]:


# keras用ライブラリ
from keras.datasets import mnist
from keras.models import Sequential, model_from_json
from keras.layers import Dense, Activation
from keras.optimizers import SGD
from keras.utils import np_utils


# In[4]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[5]:


# 舟券の配列を取得
funakenList=[]
with open(os.environ['BR_HOME']+'/boatrace/config/3t_list.dat') as f:
    reader=csv.reader(f)
    for row in reader:
        funakenList.append(row)
funakenID = [i for i in range(120)]
funakenDict=dict(zip(funakenList[0],funakenID))


# In[6]:


# 分析期間の指定は一旦ここでまとめてみる。
simStartDate="20190101"
simEndDate="20190531"


# In[7]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[8]:


# データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_rentai_v                where raceDate between '%s' and '%s'                order by raceId "               % (simStartDate,simEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("simdata:",len(loadList))


# In[9]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[10]:


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


# In[30]:


# validation向けに平均値、標準偏差を出しておく
zscore_param=xdf.describe()
# 変換の方法はこちら。
print( (xdf.loc["0":"1",["l1boat2r"] ]-zscore_param['l1boat2r']['mean'])/zscore_param['l1boat2r']['std'] )


# In[ ]:





# In[31]:


# normalizeしておく
# ★validationの時に要注意。
xdf=xdf.apply(scipy.stats.zscore, axis=0)


# In[32]:


xdf.head()


# In[33]:


# ファイルから作った辞書で変換する
ydf=df['funaken']
ydf=pd.DataFrame(ydf.replace(funakenDict))
ydf['funaken']=ydf['funaken'].astype(int)
#ydf.head()

# ydfはone-hotにしておく。
y=np.eye(120)[ydf['funaken']]
print(y)


# In[34]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
raceId_df=df['raceId'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
print(odf)
print(raceId_df)


# In[35]:


#train/testを分割
X_train, X_test, y_train, y_test,o_train,o_test,raceId_train,raceId_test = train_test_split(xdf, y,odf,raceId_df)
print("X_train,X_test:",len(X_train),len(X_test))
print(type(X_train))
print("y_train,y_test:",len(y_train),len(y_test))
print(type(y_train))
print("o_train,o_test:",len(o_train),len(o_test))
print(type(o_train))
print("raceId_train,raceId_test:",len(raceId_train),len(raceId_test))
print(type(o_train))


# In[36]:


# class
class my_Net:
    def __init__(self):
        self.Epoch = 200
        self.Batch_size = 8000
        self.Verbose = 1 #ログの出力モード切替 : 1 プログレスバーで表示
        self.output_size = 120
        self.optimize = SGD()
        #self.hidden_units = 128
        self.hidden_units = 256
        self.Validation_split = 0.2 #訓練データの中で検証データとして扱う割合
        #self.Reshape = 28 * 28
        
        self.model = Sequential()
 
    def make_net(self):
        self.model.add(Dense(self.hidden_units, input_shape=(86,)))
        self.model.add(Activation("relu"))
        self.model.add(Dense(self.hidden_units))
        self.model.add(Activation("relu"))
        self.model.add(Dense(self.hidden_units))
        self.model.add(Activation("relu"))
        self.model.add(Dense(self.hidden_units))
        self.model.add(Activation("relu"))
        self.model.add(Dense(self.output_size))
        self.model.add(Activation("softmax"))
        self.model.summary()
 
    def model_compile(self):
        self.model.compile(loss="categorical_crossentropy", #交差エントロピー誤差関数
                           optimizer=self.optimize,#確率的勾配下降法
                           metrics=["accuracy"])
 
    def make_model(self):
        self.make_net()
        self.model_compile()
 
    def train(self, x, t):
        self.model.fit(x, t, batch_size=self.Batch_size,
                       epochs=self.Epoch,
                       verbose=self.Verbose,
                       validation_split=self.Validation_split)
 
    def score(self, x, t):
        return self.model.evaluate(x, t, verbose=self.Verbose)


# In[37]:


net = my_Net()
 
net.make_model()
 
net.train(X_train, y_train)
    
score = net.score(X_test, y_test)
 
print("\nTest loss:", score[0])
print("\nTest accuracy:", score[1])


# In[38]:


#モデルを保存
model_path=os.path.join(os.environ['BR_HOME'],"boatrace/models")
model_modelfile=os.path.join(model_path,'keras_perceptron_model.json')
model_weightfile=os.path.join(model_path,'keras_perceptron_weight.json')

open(model_modelfile,"w").write(net.model.to_json())
net.model.save_weights(model_weightfile)


# In[ ]:


# testの回収率をシミュレート
# オッズを見て判断する場合
resAmount=0
buyAmount=0
resCnt=0
buyCnt=0

testPredictList=net.model.predict(X_test,batch_size=len(X_test))

for i in range(len(raceId_test) ):
    raceId=raceId_train[i]
    with dbh.cursor() as cursor:
        sel_sql = "select funaken,odds from raceodds                    where oddsType = '3t'                    and raceId = '%s'                    order by funaken"                    % (raceId)

        cursor.execute(sel_sql)
        loadList=pd.DataFrame(cursor.fetchall())
        loadList=pd.DataFrame(loadList.replace(funakenDict))
                
    for j in range(120):
        # y_predの閾値を下げてみる。
        if testPredictList[i][j]> 0.08 and ( (testPredictList[i][j] * (loadList[loadList['funaken']==j]['odds'])).values[0] > 1.5) :
            print("buy:",raceId,i,j,loadList[loadList['funaken']==j]['odds'].values[0],round(testPredictList[i][j],3) )
            buyAmount+=1
            buyCnt+=1
            if list(y_test[i]).index(1)==j:
                print("☆hit!☆:",raceId,j,loadList[loadList['funaken']==j]['odds'].values[0])
                resAmount += o_test[i]
                resCnt+=1
            else:
                pass
#res=net.model.predict_on_batch(xdf[1:3])


# In[ ]:


print("resultReturn:",resAmount/buyAmount)
print("totalRace,buy,return",len(y_test),buyAmount,resAmount )


# In[ ]:





# In[ ]:




