#!/usr/bin/env python
# coding: utf-8

# In[36]:


# ToDo 選手情報・過去レース情報から3連単舟券120種をクラス分類する

# 汎用ライブラリのimport
import sys
import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm

import tensorflow as tf


# In[37]:


# 自作ライブラリのimport
if os.environ['BR_HOME']+"/boatrace" not in sys.path:
    sys.path.append(os.environ['BR_HOME']+"/boatrace")
#print(sys.path)

from setup.myUtil import dbHandler


# In[38]:


# 分析期間の指定は一旦ここでまとめてみる。
trainStartDate="20180101"
trainEndDate="20180531"
testStartDate="20180401"
testEndDate="20180430"


# In[39]:


dbh=dbHandler.getDBHandle()
#dbHandler.closeDBHandle(dbh)


# In[40]:


# trainの元データを取得
# Todo 階級も入れて、get_dummiesする。
with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_v                where raceDate between '%s' and '%s'                order by raceId "               % (trainStartDate,trainEndDate)
    cursor.execute(sel_sql)
    loadList=cursor.fetchall()
print("traindata:",len(loadList))

with dbh.cursor() as cursor:
    sel_sql = "select * from raceabst_forml_v                where raceDate between '%s' and '%s'                order by raceId "               % (testStartDate,testEndDate)
    cursor.execute(sel_sql)
    testLoadList=cursor.fetchall()
print("testdatta:",len(testLoadList))


# In[41]:


df = pd.io.json.json_normalize(loadList)
df.head()


# In[42]:


testdf = pd.io.json.json_normalize(testLoadList)
testdf.head()


# In[87]:


# 入力のデータ整形
xdf=df.drop(['funaken','odds','raceId','raceDate'],axis=1)
xdf=pd.get_dummies(xdf,columns=['l1rank','l2rank','l3rank','l4rank','l5rank','l6rank'])
#xdf.head()
xdf.describe()

# サンプル確認用
xdf_sample=xdf[0:5]


# In[44]:


# 入力のデータ整形
testxdf=testdf.drop(['funaken','odds','raceId','raceDate'],axis=1)
testxdf=pd.get_dummies(testxdf,columns=['l1rank','l2rank','l3rank','l4rank','l5rank','l6rank'])
testxdf.head()


# In[130]:


# 結果のOne-Hot表現を作る
ydf=df['funaken']
ydf=pd.get_dummies(ydf,columns=['funaken'])
#ydf.head()
ydf.describe()

# サンプル確認用
#ydf_sample=ydf[0:5]
#ydf.head()


# In[46]:


# 結果のOne-Hot表現を作る
testydf=testdf['funaken']
testydf=pd.get_dummies(testydf,columns=['funaken'])
testydf.head()


# In[47]:


#xAtrNum=62
#yclassNum=120

# create the model
## 保存しておく
#x = tf.placeholder(tf.float32,[None,xAtrNum])
#W = tf.Variable(tf.random_uniform([xAtrNum,yclassNum],-1.0,1.0))
#b = tf.Variable(tf.random_uniform([yclassNum],-1.0,1.0))
#y = tf.nn.softmax( (tf.matmul(x,W)+b) - tf.reduce_max(tf.matmul(x,W)+b)  )


# In[123]:


xAtrNum=62
yclassNum=120

# create the model
## 保存しておく
#x = tf.placeholder(tf.float32,[None,xAtrNum])
#W = tf.Variable(tf.random_uniform([xAtrNum,yclassNum],-1.0,1.0))
#b = tf.Variable(tf.random_uniform([yclassNum],-1.0,1.0))
#y = tf.nn.softmax( (tf.matmul(x,W)+b) - tf.reduce_max(tf.matmul(x,W)+b)  )

# layerNumは2以上。
layerNum=5
layerClassNum=360
wInitMin= -0.1
wInitMax= 0.1
bInitMin= -0.1
bInitMax= 0.1

## 多層化
x = tf.placeholder(tf.float32,[None,xAtrNum])
x_hidden=[]
W_hidden=[]
b_hidden=[]

# 0 と最後については形が違うので個別に設定。
x_hidden.append(tf.Variable(tf.random_uniform([len(loadList),layerClassNum],-1.0,1.0)))
W_hidden.append(tf.Variable(tf.random_uniform([xAtrNum,layerClassNum],wInitMin,wInitMax)))
b_hidden.append(tf.Variable(tf.random_uniform([layerClassNum],bInitMin,bInitMax)))

for i in range(1,layerNum):
    x_hidden.append(tf.Variable(tf.random_uniform([len(loadList),layerClassNum],-1.0,1.0)))
    W_hidden.append(tf.Variable(tf.random_uniform([layerClassNum,layerClassNum],wInitMin,wInitMax)))
    b_hidden.append(tf.Variable(tf.random_uniform([layerClassNum],bInitMin,bInitMax)))

x_hidden[0]=tf.sigmoid(tf.matmul(x,W_hidden[0])+b_hidden[0])
for i in range(1,layerNum):
    x_hidden[i]=tf.sigmoid(tf.matmul(x_hidden[i-1],W_hidden[i])+b_hidden[i])

# 0 と最後については形が違うので個別に設定。
W = tf.Variable(tf.random_uniform([layerClassNum,yclassNum],wInitMin,wInitMax))
b = tf.Variable(tf.random_uniform([yclassNum],bInitMin,bInitMax))

y = tf.nn.softmax( (tf.matmul(x_hidden[layerNum-1],W)+b) - tf.reduce_max(tf.matmul(x_hidden[layerNum-1],W)+b)  )
#y = tf.nn.softmax( tf.sigmoid(tf.matmul(x_hidden[layerNum-1],W)+b))


# In[124]:


# define loss and optimizer
y_ = tf.placeholder(tf.float32,[None,yclassNum])
cross_entropy=-tf.reduce_sum(y_*tf.log( tf.clip_by_value(y,1e-5,1e+5) ))

# L2正則化
lambda_2=0.01
L2_sqr=tf.nn.l2_loss(W)
for i in range(layerNum):
    L2_sqr+=tf.nn.l2_loss(W_hidden[i])

loss=cross_entropy+lambda_2*L2_sqr

#cross_entropy=-tf.reduce_sum( (y_-y)**2 )
train_step=tf.train.GradientDescentOptimizer(0.1).minimize(loss)

sess = tf.Session()


# In[125]:


# tensorboard
with tf.name_scope('summary'):
    tf.summary.scalar('cross_entropy', cross_entropy)
    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter('/home/ec2-user/boatrace/log/tensorboard', sess.graph)


# In[126]:


# train
maxEpochs=1000

init = tf.global_variables_initializer()
sess.run(init)
for i in range(maxEpochs):
    sess.run(train_step,feed_dict={x:xdf.values,y_:ydf.values})
    if i % (maxEpochs/10) == 0:
        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print("cross_entropy:"+str(sess.run(cross_entropy,feed_dict={x:xdf.values,y_:ydf.values}) ),               "loss:"+str(sess.run(loss,feed_dict={x:xdf.values,y_:ydf.values})),                "accuracy:"+str(sess.run(accuracy, feed_dict={x: xdf.values, y_: ydf.values})) )
        #print("w:",sess.run(tf.reduce_sum(W),feed_dict={x: xdf.values, y_: ydf.values}))
        print("Ymax:",sess.run(tf.reduce_max(y) ,feed_dict={x:xdf.values,y_:ydf.values}))
        print("Ymin:",sess.run(tf.reduce_min(y) ,feed_dict={x:xdf.values,y_:ydf.values}))
        print("W:",sess.run(tf.reduce_sum(W) ,feed_dict={x:xdf.values,y_:ydf.values}))
        for j in range(layerNum):
            print("X%d:" % (j),sess.run(tf.reduce_max(x_hidden[j]) ,feed_dict={x:xdf.values,y_:ydf.values}))
        #print("b:",sess.run(tf.reduce_sum(b) ,feed_dict={x:xdf.values,y_:ydf.values}))
print("sample:",sess.run(x_hidden[0],feed_dict={x:xdf_sample.values,y_:ydf_sample.values}))
        


# In[128]:


print("sample:",sess.run(x_hidden[layerNum-1],feed_dict={x:xdf_sample.values,y_:ydf_sample.values}))
print("Y:",sess.run(y,feed_dict={x:xdf_sample.values,y_:ydf_sample.values}))


# In[80]:


# evaluate trained_data
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(sess.run(accuracy, feed_dict={x: testxdf.values, y_: testydf.values}))


# In[53]:


# メモリ使用チェック
print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
print(" ------------------------------------ ")
for var_name in dir():
    if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 1000: #ここだけアレンジ
        print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))


# In[ ]:




