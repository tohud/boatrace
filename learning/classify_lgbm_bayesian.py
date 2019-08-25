#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 選手情報・過去レース情報から3連単舟券120種をクラス分類する
# こちらではパラメタのベイズ最適化を試みる。
# スタートタイムや過去の連対率。逆に、オッズは消してみる。

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

from bayes_opt import BayesianOptimization
from sklearn.model_selection import StratifiedKFold
from scipy.stats import rankdata
from sklearn import metrics
import warnings


# In[2]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[3]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20170901"
trainEndDate="20181231"
# test はtrainからsplitする


# In[4]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[5]:


# trainの元データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_rentai_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("traindata:",len(loadList))


# In[6]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[7]:


# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
# オッズから作ったスコアは効きすぎるので捨ててみる
#xdf=xdf.drop(['l1score','l2score','l3score','l4score','l5score','l6score'],axis=1)
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


# In[8]:


# 結果のOne-Hot表現を作る⇒LGBMは数値配列なので数字にする。
ydf=df['funaken']
yLabel = LabelEncoder()
yLabel = yLabel.fit(ydf)
ydf = pd.DataFrame(yLabel.transform(ydf))
#ydf = yLabel.transform(ydf)
#ydf=pd.get_dummies(ydf,columns=['funaken'])
ydf.head()
#ydf.describe()


# In[ ]:





# In[ ]:


# 重み付けのため、オッズのリストを作る
#odf=df['odds'].values
odf=pd.DataFrame(df['odds'])
#odf.describe()
print(type(odf))


# In[ ]:


bayesian_tr_index, bayesian_val_index  = list(StratifiedKFold(n_splits=2, shuffle=True, random_state=1).split(xdf, ydf))[0]


# In[ ]:


def LGB_bayesian(
    num_leaves, #int
    min_data_in_leaf, #int
    reg_alpha,
    reg_lambda,
    max_depth #int
):
    
    # 整数じゃないといけないパラメータ。
    num_leaves = int(num_leaves)
    min_data_in_leaf = int(min_data_in_leaf)
    max_depth = int(max_depth)    
    assert type(num_leaves)==int
    assert type(min_data_in_leaf)==int
    assert type(max_depth)==int
    
    params={
        # 多値分類問題
        'objective': 'multiclass',
        'num_boost_round':500,
        # クラス数は 120
        'num_class': 120,
        #'class_weight':'balanced',
        #'random_state':999,
        # 以下、ハイパーパラメタ
        'max_depth':max_depth,
        'num_leaves':num_leaves,
        'min_data_in_leaf':min_data_in_leaf,
        # 正則化
        'reg_alpha':reg_alpha,
        'reg_lambda':reg_lambda,
    }

    xg_train = lgb.Dataset(xdf.iloc[bayesian_tr_index],ydf.iloc[bayesian_tr_index])
    xg_valid = lgb.Dataset(xdf.iloc[bayesian_val_index],ydf.iloc[bayesian_val_index])

    evals_result = {}
    num_round = 5000
    clf = lgb.train(params, xg_train, num_round, valid_sets = [xg_valid], verbose_eval = 250 ,early_stopping_rounds = 50,evals_result=evals_result)
    #print(evals_result['eval']['multi_logloss'])
    #print(evals_result['valid_0']['multi_logloss'])
    print(min(evals_result['valid_0']['multi_logloss']))

    predictions = clf.predict(xdf.iloc[bayesian_val_index], num_iteration=clf.best_iteration)   
    
    #score = metrics.roc_auc_score(xdf.iloc[bayesian_val_index],predictions)
    # 精度 (Accuracy) を計算する
    #print(predictions)
    score=1/min(evals_result['valid_0']['multi_logloss'])
 
    return score


# In[ ]:


bounds_LGB={
    'max_depth':(2,15),
    'min_data_in_leaf':(0,500),
    'num_leaves':(3,20),
    'reg_alpha':(0,10.0),
    'reg_lambda':(0,10.0)
}


# In[ ]:


#LGB_BO = BayesianOptimization(LGB_bayesian, bounds_LGB, random_state=13)
LGB_BO = BayesianOptimization(LGB_bayesian, bounds_LGB)
print(LGB_BO.space.keys)


# In[ ]:





# In[ ]:





# In[ ]:


init_points = 5
n_iter = 10

with warnings.catch_warnings():
    warnings.filterwarnings('ignore')
    LGB_BO.maximize(init_points=init_points, n_iter=n_iter, acq='ucb', xi=0.0, alpha=1e-6)


# In[ ]:





# In[ ]:




