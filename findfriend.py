#!/usr/bin/python
# coding: utf-8

import numpy as np
import pymongo
from pymongo import MongoClient
import operator
from math import sqrt
import pprint

user = range(3)
conf_file='eb.conf'
f = open(conf_file, 'r')
for line in f: 
  line = line.rstrip()
  user = line.split(', ')

client = MongoClient('54.153.41.222', 27017)
db = client['ValleyRain']
db.authenticate(user[1], user[2])
collection = db['UserProfile'] 

class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

def findFriend(username):
    record = collection.find_one({'name':username})
    if not record:
 	print 'Unknown user'
     	return 

    if record['attend_times'] <= 1:
        print 'User %s just attended once. Need more data.' %(username)
        return

    similarityScoreDict = {}
    attendDict = record['attended']
    normAttendDict = calNorm(attendDict)

    for entry in collection.find():
        if entry['attend_times'] <= 1:
            continue    
        pairAttendDict = entry['attended']
        normPairAttendDict = calNorm(pairAttendDict)
        crossProduct = crossProd(attendDict, pairAttendDict)
        similarityScore = crossProduct / (normAttendDict * normPairAttendDict)
        if similarityScore:
            similarityScoreDict[entry['name']] = similarityScore
        
    return sorted(similarityScoreDict.items(), key=operator.itemgetter(1), reverse=True)[0:20]
        
def calNorm(dict):
    res = 0;
    for x in dict.keys():
        if dict[x] == 'Checked In':
            res = res + 1 * 1
        elif dict[x] == 'Attending':
            res = res + 0.5 * 0.5
        elif dict[x] == 'Not Attending':
            res = res + 0.25 * 0.25
    return sqrt(res)    

def crossProd(dict1, dict2):
    res = 0
    
    for x in dict1.keys():
        a = 0
        if x in dict2.keys():
            b = 0
            if dict1[x] == 'Checked In':
                a = 1
            elif dict1[x] == 'Attending':
                a = 0.5
            elif dict1[x] == 'Not Attending':
                a = 0.25
            
            if dict2[x] == 'Checked In':
                b = 1
            elif dict2[x] == 'Attending':
                b = 0.5
            elif dict2[x] == 'Not Attending':
                b = 0.25
            
            res = res + a * b
    
    return res

while(1):
    name=raw_input("Who do you want to check('exit' to exit):")
    if name == 'exit':
       break

    name= name.title()
    #Detect he name is in the database or not.
    result = collection.find_one({'name': name})
    if result:
       MyPrettyPrinter().pprint(result)
    
    print '\nUser Correlations:\n'

    result = findFriend(name) 
    if result:
       MyPrettyPrinter().pprint(result)
            
