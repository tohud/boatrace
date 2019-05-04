#!/usr/bin/env python
# coding: utf-8

# In[9]:


# ToDo 選手情報・過去レース情報から3連単舟券120種をクラス分類する

# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm

import tensorflow as tf


# In[2]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[3]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20180201"
trainEndDate="20180228"
testStartDate="20180301"
testEndDate="20180331"


# In[4]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[6]:


# trainの元データを取得
# Todo 階級も入れて、get_dummiesする。
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print(len(loadList))


# In[7]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[20]:


# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
xdf.head()


# In[22]:


# 結果のOne-Hot表現を作る
ydf=df['funaken']
ydf=pd.get_dummies(ydf,columns=['funaken'])
ydf.head()


# In[25]:


xAtrNum=38
yclassNum=120
# create the model
x = tf.placeholder(tf.float32,[None,xAtrNum])
#W = tf.Variable(tf.zeros([xAtrNum,yclassNum]))
#b = tf.Variable(tf.zeros([yclassNum]))
W = tf.Variable(tf.random_uniform([xAtrNum,yclassNum],-1.0,1.0))
b = tf.Variable(tf.random_uniform([yclassNum],-1.0,1.0))
y = tf.nn.softmax(tf.matmul(x,W)+b )


# In[28]:


# define loss and optimizer
y_ = tf.placeholder(tf.float32,[None,yclassNum])
#cross_entropy=-tf.reduce_sum(y_*tf.log(y))
cross_entropy=-tf.reduce_sum( (y_-y)**2 )
train_step=tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)


# In[29]:


# train
init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)
for i in range(100):
    sess.run(train_step,feed_dict={x:xdf.values,y_:ydf.values})
    print(sess.run(cross_entropy,feed_dict={x:xdf.values,y_:ydf.values}))


# In[ ]:





# In[30]:


# メモリ使用チェック
print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
print(" ------------------------------------ ")
for var_name in dir():
    if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 1000: #ここだけアレンジ
        print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))


# In[ ]:




