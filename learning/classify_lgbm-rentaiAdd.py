#!/usr/bin/env python
# coding: utf-8

# In[1]:


# todo 学習結果を使って運用するための環境を作る。

# 選手情報・過去レース情報から3連単舟券120種をクラス分類する
# LGBMでやってみる。
# todo:bayseの方と、インプットの与え方をあわせる。今はOne-Hotが一致していない。
# 的中予想確率x%以上のうち、オッズで見合うものだけ買った場合のシミュレーションをする。

# このnoteでは情報を増やしてみる。過去100レースの着順分布をいれる。m1rank1,m1rank2,…m1rank6,m2rank1,…,m6rank6
# 期間を変えるときには、num_leavesも調整する。

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
from itertools import chain


# In[2]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[3]:


# 舟券の配列を取得
funakenList=[]
with open(os.environ['BR_HOME']+'/boatrace/config/3t_list.dat') as f:
    reader=csv.reader(f)
    for row in reader:
        funakenList.append(row)
funakenID = [i for i in range(120)]
funakenDict=dict(zip(funakenList[0],funakenID))
#print(funakenDict)


# In[4]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20170901"
trainEndDate="20181231"
# test はtrainからsplitする
testStartDate="20190101"
testEndDate="20190531"


# In[5]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[6]:


# trainの元データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_rentai_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("traindata:",len(loadList))


# In[ ]:





# In[7]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[28]:


# 入力のデータ整形
#xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
#xdf=pd.get_dummies(xdf,columns=['l1rank','l2rank','l3rank','l4rank','l5rank','l6rank'])
#xdf.head()

# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
# オッズから作ったスコアは効きすぎるので捨ててみる
xdf=xdf.drop(['l1score','l2score','l3score','l4score','l5score','l6score'],axis=1)
#xdf=xdf.drop(['l1Fcnt','l2Fcnt','l3Fcnt','l4Fcnt','l5Fcnt','l6Fcnt'],axis=1)
#xdf=xdf.drop(['l1oldavgstdev','l2oldavgstdev','l3oldavgstdev','l4oldavgstdev','l5oldavgstdev','l6oldavgstdev'],axis=1)

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


# In[29]:


xdf.describe()


# In[ ]:





# In[30]:


# ファイルから作った辞書で変換する
ydf=df['funaken']
ydf=pd.DataFrame(ydf.replace(funakenDict))
ydf['funaken']=ydf['funaken'].astype(int)
#print(ydf.head())
print(ydf['funaken'].dtype)


# In[31]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
#print(odf)


# In[ ]:





# In[32]:


X_train, X_test, y_train, y_test,o_train,o_test = train_test_split(xdf, ydf,odf)
print("X_train,X_test:",len(X_train),len(X_test))


# In[33]:


lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)


# In[34]:


lgbm_params = {
    # 多値分類問題
    'objective': 'multiclass',
    'num_boost_round':250,
    # クラス数は 120
    'num_class': 120,
    #'class_weight':'balanced',
    #'random_state':999,
    # 以下、ハイパーパラメタ
    'max_depth':2,
    'num_leaves':3,
    'min_data_in_leaf':300,
    # 正則化
    'reg_alpha':6.161,
    'reg_lambda':8.977,
}


# In[35]:


lgb.LGBMClassifier()


# In[36]:


model = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_eval)


# In[37]:


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


# In[38]:


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


# In[39]:


print("totalRace,buy,return,",len(y_test),buyAmount,resAmount ,resAmount/buyAmount)
# 現状でも100%はロバストに超えそう。←random_state入れてただけ。。random_state=999
# だがrrが1.2でもbuyが6/300レースだと、1000円投票しても一日だと約3000*1.2⇒利益600円なので、もっと回収率を上げるか母数増やす。
# totalRace,buy,return 28274 608 614.3
# totalRace,buy,return 28274 614 804.8

#項目を減らしてみる。
#totalRace,buy,return, 17925 151 153.29999999999998 1.0152317880794701


# In[40]:


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
        # y_predの閾値を下げてみる。
        if y_pred[i][j]> 0.05 and ( (y_pred[i][j] * (loadList[loadList['funaken']==j]['odds'])).values[0] > 1.5) :
            print("buy:",raceId,i,j,loadList[loadList['funaken']==j]['odds'].values[0],round(y_pred[i][j],3) )
            buyAmount+=1
            if y_test['funaken'].iloc[i]==j:
            #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
                print("☆hit!☆:",raceId,j,loadList[loadList['funaken']==j]['odds'].values[0])
                resAmount += o_test[i]
            else:
            #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
                pass
#print("resultReturn:",resAmount/buyAmount)
#print("totalRace,buy,return",len(y_test),buyAmount,resAmount )

# y_pred[i][j]> 0.05に閾値下げてみた。投票数はかなり増えているが、回収率が低く、トータルリターンは下がっている。
# ToDo：運用に向けてはこのバランスを調整してみるのはあり。
#resultReturn: 1.005279187817259
#totalRace,buy,return 28274 4925 4951.0

#resultReturn: 0.8838785046728972
#totalRace,buy,return 17925 6848 6052.8
#resultReturn: 0.8059009786989055
#totalRace,buy,return 17925 6948 5599.399999999996

#resultReturn: 0.8867549668874173
#totalRace,buy,return 17925 5587 4954.3

# 以下、入力項目を落としてみる。ボート、モーター、過去順位、スタートタイムだけ残す
#resultReturn: 0.9442170972776139
#totalRace,buy,return 17925 5767 5445.299999999999

#resultReturn: 0.8314920965780791
#totalRace,buy,return 17925 5757 4786.9000000000015

# パラメタ変更
#resultReturn: 0.86511287964918
#totalRace,buy,return 17925 6157 5326.500000000002

# 切り捨てに変更
#resultReturn: 0.8563023801542073
#totalRace,buy,return 17925 5966 5108.700000000001


# In[41]:


print("resultReturn:",resAmount/buyAmount)
print("totalRace,buy,return",len(y_test),buyAmount,resAmount )


# In[42]:


# trainの回収率を計算
y_pred = model.predict(X_train, num_iteration=model.best_iteration)
y_pred_max = np.argmax(y_pred, axis=1)  # 最尤と判断したクラスの値にする

#print(X_train.head())
#print(y_train[0:5])
#print(y_pred_max[0:5])
#c = collections.Counter(y_pred_max)
#print(len(c) )

# 精度 (Accuracy) を計算する
# エラーになるけど気にしない。
#accuracy = sum(y_train == y_pred_max) / len(y_train)
#print("accuracy:",accuracy)

# 回収率を計算
#res=0
#for i in range(len(y_train)):
#    if y_train.iloc[i]==y_pred_max[i]:
#        res += o_train[i] -1
#    else:
#        pass
#print("return:",res/len(y_train))


# In[43]:


print(y_pred[0])


# In[44]:


print(df.iloc[X_train.index]['raceId'])


# In[ ]:





# In[45]:


print(xdf.columns)


# In[46]:


print(model.feature_importance())


# In[ ]:





# In[ ]:




