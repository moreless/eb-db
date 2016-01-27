#!/usr/bin/python
# coding: utf-8

import csv
import sys
import re
import pymongo
from pymongo import MongoClient
import pprint

reload(sys)
sys.setdefaultencoding('utf-8')

'''
    Initialize the DataBase
'''

class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

user = range(3)
conf_file='eb.conf'
f = open(conf_file, 'r')
for line in f: 
  line = line.rstrip()
  user = line.split(', ')

        
client = MongoClient('localhost', 27017)
db = client['ValleyRain']
db.authenticate(user[1], user[2])
collection = db['UserProfile']    

while(1):
    #name="Lanchao Liu"
    name = raw_input("Who do you want to check('exit' to exit):")
    if name == 'exit':
       break

    name= name.title()
    #Detect he name is in the database or not.

    result = collection.find_one({'name': name})
    if result:
       MyPrettyPrinter().pprint(result)

