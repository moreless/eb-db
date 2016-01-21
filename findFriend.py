import numpy as np
import pymongo
from pymongo import MongoClient
import operator
        
client = MongoClient('localhost', 27017)
db = client['ValleyRain']
collection = db['UserProfile'] 

def findFriend(username):
    record = collection.find_one({'name':username})
    if record['attend_times'] <= 1:
        print 'User %s just attended once. Need more data.' %(username)
        return

    similarityScore = {}
    attendList = record['attend_times']
    for entry in collection.find():
        if entry['attend_times'] <= 1:
            pass    
        parAttendList = entry['attended']
    
