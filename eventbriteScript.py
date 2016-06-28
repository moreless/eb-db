#!/usr/bin/python
# coding: utf-8

import requests
import sys
import re
import calendar
import dateutil.parser
from datetime import datetime, timedelta

import pymongo
from pymongo import MongoClient

notprintall = False

def findAnswers(answers):
	'''
		This funciton is used to find the wechatID, hobby, company and job.
	'''
	ans=['','','','','','','']
	if not answers:
		print 'Errors! No answers found in this entry.\n'
		return

	for entry in answers:
		wechatID = ''
		hobby    = ''
		company  = ''
		job      = ''

		if re.search('wechat ID', entry['question'], re.I):
			if 'answer' in entry:
				ans[0] = entry['answer']
		elif re.search('Hobbies', entry['question'], re.I):
			if 'answer' in entry:
				ans[1] = entry['answer']
		elif re.search('company', entry['question'], re.I):
			if 'answer' in entry:
				ans[2] = entry['answer']
		elif re.search('Position', entry['question'], re.I):
			if 'answer' in entry:
				ans[3] = entry['answer']
		elif re.search('Categroies of Books', entry['question'], re.I):
			if 'answer' in entry:
				ans[4] = entry['answer']
		elif re.search('The city you live', entry['question'], re.I):
			if 'answer' in entry:
				ans[5] = entry['answer']
		if re.search('First time com', entry['question'], re.I):
		    if 'answer' in entry:
			ans[6] = entry['answer']
	
	return ans

def get_register_data(response, i, filename, event_name, flag):
	dataEntry    = response.json()['attendees'][i]
	
	user_profile = dataEntry['profile']
	answers      = dataEntry['answers']
	status       = dataEntry['barcodes'][0]['status']
	est_time     = dataEntry['barcodes'][0]['created']
	
	'''
		The following fields are from 'profile'.
	'''
	name  = user_profile['name'].title()
	
	if 'email' in user_profile:
		email = user_profile['email'].lower()
	else:
		email = ''
	
	if not email:
		print '[Warning]The user %s do not provide an email address!\n' % (name)
		return 
	
	'''
		The following fields are from 'answers'.
	'''
	
	ans = findAnswers(answers)
	wechatID= ans[0]
	hobby=ans[1]
	company=ans[2]
	job=ans[3]
	books=ans[4]
	city = ans[5]
	first_time = ans[6]

	#print wechatID, hobby,company,job
	'''
		The following fields are inferred from records. 
	'''
	eventID = dataEntry['event_id']
	status  = dataEntry['status']
	
	userRecord = collection.find_one({'email': email})
	
	if not userRecord:
	  attended={}
	  attended[event_name]=status
	  id = collection.count() + 1
	  first = event_name
		 
	  collection.insert({
			   'name'    : name,
			   'email'   : email,
			   'wechatID': wechatID,
               'company' : company,
               'job'     : job,
               'first'   : first,
               'hobby'   : hobby,
               'books'   : books,
               'attended': attended,
               'ID'      : id,
               'city'    : city,
               'attend_times' : 1,
			   })
	  print "Successfully insert a new record."
	else:
		#print userRecord
		attended = userRecord['attended']
		attended[event_name]=status
		attend_times = len(attended.keys())
		if first_time == 'Yes':  #for some one registered using gform before but forgot.
			collection.update_one(
		          {'email': email},
		          {
		            "$set" :  {'name': name,
		                       'wechatID' : wechatID,
		                       'hobby'  : hobby,
		                       'company' : company,
		                       'job'     : job,
		                       'books'   : books,
		                       'attended': attended,
		                       'city'    : city,
		                       'attend_times' : attend_times,
		                      },
		          }
		      )
		if userRecord['first'] == '':
			first = event_name
			collection.update_one(
		          {'email': email},
		          {
		            "$set" :  {'name': name,
		                       'first' : first,
		                       'attended': attended,
		                       'attend_times' : attend_times,
		                      },
		          }
		      )
		else:
			collection.update_one(
		          {'email': email},
		          {
		            "$set" :  {
		                      'name': name,
		                      'attended': attended,
		                      'attend_times' : attend_times,
		                      },
		          }
		      )
		print "Successfully update a record."
			
	utc_date = dateutil.parser.parse(est_time)
	date = utc_to_local(utc_date)

	if flag:
		i=i+50

	try:
		user_profile['email']
		print i+1, user_profile['name'], user_profile['email'], status, date
		str='%d,%s,%s, %s, %s\n' % (i+1, user_profile['name'], user_profile['email'], status, date)
	except:
		print i+1, user_profile['name'], status, date
		str='%d,%s,%s, %s\n' % (i+1, user_profile['name'], status, date)

	with open(filename, 'a+') as  output_file:
		output_file.write(str)


	
def utc_to_local(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def add_quote(str):
	return '"'+str+'"'


'''
	Main logic of the program. 
'''

'''
    Initialize the DataBase
'''
   
user = range(3)
conf_file='eb.conf'
f = open(conf_file, 'r')
for line in f: 
  line = line.rstrip()
  user = line.split(', ')
  key = user[0]


client = MongoClient('localhost', 27017)
db = client['ValleyRain']
#db.authenticate(user[1], user[2])
collection = db['UserProfile'] 

reload(sys)
sys.setdefaultencoding('utf-8')

filename = 'guest.csv'

# Get the whole events response.

response_event = requests.get(
    "https://www.eventbriteapi.com/v3/users/me/owned_events/",

    headers = {
        "Authorization": key,
    },
    verify = True,  # Verify SSL certificate
)


# Get the attendees for each events. 
for j in range(response_event.json()["pagination"]["object_count"]):
	pass

	#comment for traverse all events
	if j<response_event.json()["pagination"]["object_count"]-1 and notprintall:
		continue
	#j=j-1

	print response_event.json()["events"][j]["name"]["text"]
	#event_name = response_event.json()["events"][j]["name"]["text"]
	event_name= re.findall(u'(《.+?》)', response_event.json()["events"][j]["name"]["text"])

		# Get the information for each page. 
		# TODO: How about n > 100? mod 50
	response = requests.get(
	    "https://www.eventbriteapi.com/v3/events/"+response_event.json()["events"][j]["id"]+"/attendees/",
	    headers = {
	        "Authorization": key,
	    },
	    verify = True,  
	)

	if 'object_count' in response.json()["pagination"]:
		object_count= response.json()["pagination"]["object_count"]
		print object_count, "registered"
	else:
		object_count=0
		print 'nobody registered yet.'

	if (object_count>50):

		response2 = requests.get(
			"https://www.eventbriteapi.com/v3/events/" + response_event.json()["events"][j]["id"] + "/attendees/?page=2",
			headers={
			    "Authorization": key,
			},
			verify=True,  
			)
				
	with open(filename, 'a+') as  output_file:
					output_file.write(response_event.json()["events"][j]["name"]["text"]+'\n')

	# Get the information for each attendees. 
	for i in range (object_count):
		if (i<50):
			get_register_data(response, i, filename, event_name[0], False)
		else:
			get_register_data(response2, i-50, filename, event_name[0], True)
