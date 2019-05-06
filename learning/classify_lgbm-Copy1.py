#!/usr/bin/env python
# coding: utf-8

# In[156]:


# 選手情報・過去レース情報から3連単舟券120種をクラス分類する
# LGBMでやってみる。
# めでたく、激しく過学習

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


# In[119]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[120]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20180101"
trainEndDate="20180731"
# test はtrainからsplitする


# In[121]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[122]:


# trainの元データを取得
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("traindata:",len(loadList))


# In[123]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[124]:


# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
xdf=pd.get_dummies(xdf,columns=['l1rank','l2rank','l3rank','l4rank','l5rank','l6rank'])
xdf.head()


# In[125]:


# 結果のOne-Hot表現を作る
ydf=df['funaken']
yLabel = LabelEncoder()
yLabel = yLabel.fit(ydf)
#ydf = pd.DataFrame(yLabel.transform(ydf))
ydf = yLabel.transform(ydf)
#ydf=pd.get_dummies(ydf,columns=['funaken'])
#ydf.head()
#ydf.describe()


# In[ ]:





# In[126]:


# 重み付けのため、オッズのリストを作る
odf=df['odds'].values
#odf=pd.DataFrame(df['odds'])
#odf.describe()
print(type(odf))


# In[148]:


X_train, X_test, y_train, y_test,o_train,o_test = train_test_split(xdf, ydf,odf)


# In[149]:


lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)


# In[181]:


lgbm_params = {
    # 多値分類問題
    'objective': 'multiclass',
    # クラス数は 120
    'num_class': 120,
    #'class_weight':'balanced',
    'random_state':999,
    # 以下、ハイパーパラメタ
    'max_depth':20,
    'num_leaves':3,
    # 正則化
    'reg_alpha':0.1,
    'reg_lambda':0.1,
}


# In[182]:


lgb.LGBMClassifier()


# In[183]:


model = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_eval)


# In[195]:


y_pred = model.predict(X_test, num_iteration=model.best_iteration)
y_pred_max = np.argmax(y_pred, axis=1)  # 最尤と判断したクラスの値にする

# 精度 (Accuracy) を計算する
accuracy = sum(y_test == y_pred_max) / len(y_test)
print("accuracy:",accuracy)

# 回収率を計算
res=0
for i in range(len(y_test)):

    if y_test[i]==y_pred_max[i]:
        #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
        res += o_test[i] -1
    else:
        #print("i:",i,"result:",y_test[i],"forecast:",y_pred_max[i],"forecastProb:",y_pred[i][y_pred_max[i]],"return:",o_test[i],"expect:",y_pred[i][y_pred_max[i]]*o_test[i])
        pass
print("resultReturn:",res/len(y_test))


# In[ ]:





# In[196]:


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
print(accuracy)

# 回収率を計算
res=0
for i in range(len(y_train)):
    if y_train[i]==y_pred_max[i]:
        res += o_train[i] -1
    else:
        pass
print(res/len(y_train))


# In[ ]:





# In[ ]:




