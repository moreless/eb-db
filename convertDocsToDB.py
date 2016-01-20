#!/usr/local/bin/python
# -- coding: UTF-8 --

'''
    This module is used to initialize the database using the csv file.
'''

'''
    Database schema:
    Name   
    Email
    wechatID
    Hobby
    Company/School
    Job
    Attended
    First
    ID:(系统分配)
'''

''' 
原CSV格式：
0. Timestamp
1. 微信ID，以便大家互相结识p
2. Email，用于接受活动通知等。Email不会公开
3. 姓名
4. 公司或学校
5. 职业
6. 兴趣爱好
7. 对读书会的小伙伴们，还有什么想说的吗？
8. 喜欢的书籍类别，以及希望在图书会推广的书目
9. 居住城市（以便大家carpool)
'''

import csv
import sys
import re
import pymongo
from pymongo import MongoClient


'''
    Initialize the DataBase
'''
        
client = MongoClient('localhost', 27017)
db = client['ValleyRain']
collection = db['UserProfile']    

#User ID in the database.
id = 1

with open ('roster.csv') as f:
    f_csv = csv.reader(f)
    headers = next(f_csv)
    for row in f_csv:
        email    = row[2]
        
        #Validate the email address format.
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not EMAIL_REGEX.match(email):
            #print id
            continue
        
        wechatID = row[1]
        name     = row[3]
        company  = row[4] 
        job      = row[5]
        hobby    = row[6]
        
        #Will update the record if existed.
        #Will create a new one if not existed.
        collection.update_one(
                              {'email': email},
                              {
                               "$set" :  {'name' :    name,
                                          'wechatID': wechatID,
                                          'company':  company,
                                          'job':      job,
                                          'first':    '',
                                          'hobby':    hobby,
                                          'attended': {},
                                          'ID':       id,
                                          'attend_times': 1
                                          }
                               },
                               True
                              )
        id = id + 1
    print "Write doc to db done!"
    f.close()
        
        
        
        
        
        
