#!/usr/bin/env python
# coding: utf-8

# In[72]:


# 選手情報・過去レース情報から3連単舟券120種をクラス分類する
# LGBMでやってみる。
# todo:bayseの方と、インプットの与え方をあわせる。今はOne-Hotが一致していない。
# 的中予想確率10%以上のうち、オッズで見合うものだけ買った場合のシミュレーションをする。

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

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import csv


# In[73]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[74]:


# 舟券の配列を取得
funakenList=[]
with open(os.environ['BR_HOME']+'/boatrace/config/3t_list.dat') as f:
    reader=csv.reader(f)
    for row in reader:
        funakenList.append(row)
funakenID = [i for i in range(120)]
funakenDict=dict(zip(funakenList[0],funakenID))
print(funakenDict)


# In[75]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20180101"
trainEndDate="20180731"
# test はtrainからsplitする


# In[164]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[77]:


# trainの元データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("traindata:",len(loadList))


# In[78]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[80]:


# 入力のデータ整形
#xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
#xdf=pd.get_dummies(xdf,columns=['l1rank','l2rank','l3rank','l4rank','l5rank','l6rank'])
#xdf.head()

# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
#xdf=pd.get_dummies(xdf,columns=['l1rank','l2rank','l3rank','l4rank','l5rank','l6rank'])
rankLabel=LabelEncoder()
rankLabel=rankLabel.fit(xdf['l1rank'])
xdf['l1rank']=rankLabel.transform(xdf['l1rank'])
xdf['l2rank']=rankLabel.transform(xdf['l2rank'])
xdf['l3rank']=rankLabel.transform(xdf['l3rank'])
xdf['l4rank']=rankLabel.transform(xdf['l4rank'])
xdf['l5rank']=rankLabel.transform(xdf['l5rank'])
xdf['l6rank']=rankLabel.transform(xdf['l6rank'])
xdf.head()


# In[ ]:





# In[ ]:





# In[109]:


# ファイルから作った辞書で変換する
ydf=df['funaken']
ydf=pd.DataFrame(ydf.replace(funakenDict))
print(ydf.head())


# In[110]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
print(odf)


# In[111]:


X_train, X_test, y_train, y_test,o_train,o_test = train_test_split(xdf, ydf,odf)


# In[112]:


lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)


# In[113]:


lgbm_params = {
    # 多値分類問題
    'objective': 'multiclass',
    # クラス数は 120
    'num_class': 120,
    #'class_weight':'balanced',
    'random_state':999,
    # 以下、ハイパーパラメタ
    'max_depth':3,
    'num_leaves':19,
    'min_data_in_leaf':300,
    # 正則化
    'reg_alpha':9.591,
    'reg_lambda':9.928 ,
}


# In[114]:


lgb.LGBMClassifier()


# In[115]:


model = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_eval)


# In[118]:


y_pred = model.predict(X_test, num_iteration=model.best_iteration)
y_pred_max = np.argmax(y_pred, axis=1)  # 最尤と判断したクラスの値にする

# 精度 (Accuracy) を計算する
accuracy = sum(y_test['funaken'] == y_pred_max) / len(y_test)
print("accuracy:",accuracy)

# 回収率を計算
res=0
for i in range(len(y_test)):
    if (y_test.iloc[i])['funaken']==y_pred_max[i]:
        #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
        res += o_test[i] -1
    else:
        #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
        pass
print("resultReturn:",res/len(y_test))


# In[170]:


print(len(y_pred))
# オッズを見て判断する場合
resAmount=0
buyAmount=0

dfIndexList=y_test['funaken'].index
for i in range(len(y_test)):
    raceId = df.iloc[dfIndexList[i]]['raceId']
    #print(raceId)
    with dbh.cursor() as cursor:
        sel_sql = "select funaken,odds from raceodds                    where oddsType = '3t'                    and raceId = '%s'                    order by funaken"                    % (raceId)
        cursor.execute(sel_sql)
        loadList=pd.DataFrame(cursor.fetchall())
        loadList=pd.DataFrame(loadList.replace(funakenDict))
    #print((loadList[loadList['funaken']==0]['odds'] * y_pred[i][0] ).values[0] )
    #if ( (loadList[loadList['funaken']==0]['odds'] * y_pred[i][0] ).values[0] > 1) :
    #    print("ok")
    #print(y_pred[i][0])
    #print(raceId)
    for j in range(120):
        if y_pred[i][j]> 0.10 and ( (y_pred[i][j] * (loadList[loadList['funaken']==j]['odds'])).values[0] > 1.5) :
            print("buy:",raceId,i,j,loadList[loadList['funaken']==j]['odds'].values[0])
            buyAmount+=1
            if y_test['funaken'].iloc[i]==j:
            #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
                print("☆hit!☆:",raceId,j,loadList[loadList['funaken']==j]['odds'].values[0])
                resAmount += o_test[i]
            else:
            #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
                pass
print("resultReturn:",resAmount/buyAmount)


# In[171]:


print("totalRace,buy,return",len(y_test),buyAmount,resAmount )


# In[100]:


# trainの回収率を計算
y_pred = model.predict(X_train, num_iteration=model.best_iteration)
y_pred_max = np.argmax(y_pred, axis=1)  # 最尤と判断したクラスの値にする

#print(X_train.head())
#print(y_train[0:5])
#print(y_pred_max[0:5])
#c = collections.Counter(y_pred_max)
#print(len(c) )

# 精度 (Accuracy) を計算する
accuracy = sum(y_train == y_pred_max) / len(y_train)
print("accuracy:",accuracy)

# 回収率を計算
res=0
for i in range(len(y_train)):
    if y_train.iloc[i]==y_pred_max[i]:
        res += o_train[i] -1
    else:
        pass
print("return:",res/len(y_train))


# In[37]:


print(y_pred[0])


# In[36]:


print(df.iloc[X_train.index]['raceId'])


# In[ ]:





# In[ ]:





# In[17]:


print(model.feature_importance())


# In[ ]:





# In[ ]:




