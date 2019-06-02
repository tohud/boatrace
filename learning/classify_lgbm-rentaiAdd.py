#!/usr/bin/env python
# coding: utf-8

# In[2]:


# todo 学習結果を使って運用するための環境を作る。

# 選手情報・過去レース情報から3連単舟券120種をクラス分類する
# LGBMでやってみる。
# todo:bayseの方と、インプットの与え方をあわせる。今はOne-Hotが一致していない。
# 的中予想確率x%以上のうち、オッズで見合うものだけ買った場合のシミュレーションをする。

# このnoteでは情報を増やしてみる。過去100レースの着順分布をいれる。m1rank1,m1rank2,…m1rank6,m2rank1,…,m6rank6
# 着順分布の取得が時間かかりすぎるので、期間を絞って開発する。★☆
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


# In[3]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[4]:


# 舟券の配列を取得
funakenList=[]
with open(os.environ['BR_HOME']+'/boatrace/config/3t_list.dat') as f:
    reader=csv.reader(f)
    for row in reader:
        funakenList.append(row)
funakenID = [i for i in range(120)]
funakenDict=dict(zip(funakenList[0],funakenID))
#print(funakenDict)


# In[5]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20170901"
trainEndDate="20190430"
# test はtrainからsplitする


# In[6]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[7]:


# trainの元データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("traindata:",len(loadList))


# In[8]:


# 過去成績をjoinする
oldResultList=[]
progressCounter=0
with dbh.cursor() as racecursor:
    for raceId in [ loadList[i]['raceId'] for i in range(len(loadList))]:
        progressCounter+=1
        if progressCounter % 1000 == 0:
            print("progress:",progressCounter/len(loadList))
        with dbh.cursor() as membercursor:
            #raceIdから登録番号のリストを取得
            selmember_sql = "select rmToban from racemember where raceId = '%s' order by rmLane" % (raceId)
            membercursor.execute(selmember_sql)
            tmpMemList=membercursor.fetchall()
            with dbh.cursor() as oldResultCursor:
                tmpOldDict={'raceId':raceId}
                lane=1
                for tobanHash in tmpMemList:
                    # あとでまた変換するのが面倒だから、変数名をレーン別にわける。
                    sel_sql = "select                                    count(CASE WHEN a.goalRank=1 THEN a.goalRank END)/100 as lane"+str(lane)+"oldRank1,                                   count(CASE WHEN a.goalRank=2 THEN a.goalRank END)/100 as lane"+str(lane)+"oldRank2,                                   count(CASE WHEN a.goalRank=3 THEN a.goalRank END)/100 as lane"+str(lane)+"oldRank3,                                   count(CASE WHEN a.goalRank=4 THEN a.goalRank END)/100 as lane"+str(lane)+"oldRank4,                                   count(CASE WHEN a.goalRank=5 THEN a.goalRank END)/100 as lane"+str(lane)+"oldRank5,                                   count(CASE WHEN a.goalRank=6 THEN a.goalRank END)/100 as lane"+str(lane)+"oldRank6                                from (                                     select tr.goalRank from raceresult tr                                    where tr.toban = '%s'                                     and tr.raceId < '%s'                                    order by tr.raceId desc                                     limit 100                                    ) a "                                % (tobanHash['rmToban'],raceId)
                    oldResultCursor.execute(sel_sql)
                    # 辞書型で、6レーン分を順次結合
                    tmpOldDict.update( (oldResultCursor.fetchall())[0] )
                    lane+=1
                # 終わったらraceId別にList型でまとめる
                oldResultList.append(tmpOldDict)
print("oldResultList:",len(oldResultList))
#print(oldResultList[0:5])


# In[9]:


df_member = pd.io.json.json_normalize(loadList)
df_oldResult = pd.io.json.json_normalize(oldResultList)
for lane in range(1,6+1):
    for Rank in range(1,6+1):
        key="lane"+str(lane)+"oldRank"+str(Rank)
        df_oldResult[key]=df_oldResult[key].astype(np.float)
df = pd.merge(df_member,df_oldResult,on='raceId',how='inner')
df.head()


# In[10]:


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


# In[11]:


xdf.describe()
#print(xdf['l1boat2r'].describe())
#print(xdf['lane1oldRank1'].describe())
#print(xdf['lane6oldRank6'].describe())


# In[ ]:





# In[12]:


# ファイルから作った辞書で変換する
ydf=df['funaken']
ydf=pd.DataFrame(ydf.replace(funakenDict))
ydf['funaken']=ydf['funaken'].astype(int)
#print(ydf.head())
print(ydf['funaken'].dtype)


# In[13]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
#print(odf)


# In[ ]:





# In[14]:


X_train, X_test, y_train, y_test,o_train,o_test = train_test_split(xdf, ydf,odf)
print("X_train,X_test:",len(X_train),len(X_test))


# In[15]:


lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)


# In[16]:


lgbm_params = {
    # 多値分類問題
    'objective': 'multiclass',
    # クラス数は 120
    'num_class': 120,
    #'class_weight':'balanced',
    #'random_state':999,
    # 以下、ハイパーパラメタ
    'max_depth':3,
    'num_leaves':6,
    'min_data_in_leaf':300,
    # 正則化
    'reg_alpha':2.425,
    'reg_lambda':9.473 ,
}


# In[17]:


lgb.LGBMClassifier()


# In[18]:


model = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_eval)


# In[19]:


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


# In[20]:


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


# In[21]:


print("totalRace,buy,return",len(y_test),buyAmount,resAmount )
# 現状でも100%はロバストに超えそう。
# だがrrが1.2でもbuyが6/300レースだと、1000円投票しても一日だと約3000*1.2⇒利益600円なので、もっと回収率を上げるか母数増やす。
# totalRace,buy,return 28274 608 614.3
# totalRace,buy,return 28274 614 804.8


# In[23]:


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
print("totalRace,buy,return",len(y_test),buyAmount,resAmount )
# y_pred[i][j]> 0.05に閾値下げてみた。投票数はかなり増えているが、回収率が低く、トータルリターンは下がっている。
# ToDo：運用に向けてはこのバランスを調整してみるのはあり。
#resultReturn: 1.005279187817259
#totalRace,buy,return 28274 4925 4951.0


# In[25]:


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


# In[26]:


print(y_pred[0])


# In[27]:


print(df.iloc[X_train.index]['raceId'])


# In[ ]:





# In[ ]:





# In[28]:


print(model.feature_importance())


# In[ ]:





# In[ ]:




