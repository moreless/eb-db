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

reload(sys)
sys.setdefaultencoding('utf-8')

def findAnswers(answers):
  ans=['','','','','','','','','']
  '''
    This funciton is used to find the wechatID, hobby, company and job.
  '''

  if not answers:
    print 'Errors! No answers found in this entry.\n'
    return

  for entry in answers:

    if re.search('Where did you hear ', entry['question'], re.I):
      if 'answer' in entry:
        ans[0] = entry['answer']
        #print where
    if re.search('First time com', entry['question'], re.I):
      if 'answer' in entry:
        ans[1] = entry['answer']
        #print ans[1]
    if re.search('wechat ID', entry['question'], re.I):
      if 'answer' in entry:
        ans[2] = entry['answer']
        #print wechat_id
    elif re.search('Hobbies', entry['question'], re.I):
      if 'answer' in entry:
        ans[3] = entry['answer']

    elif re.search('Categroies of Books', entry['question'], re.I):
      if 'answer' in entry:
        ans[4] = entry['answer']

    elif re.search('Company', entry['question'], re.I):
      if 'answer' in entry:
        ans[5] = entry['answer']

    elif re.search('Position', entry['question'], re.I):
      if 'answer' in entry:
        ans[6] = entry['answer']

    elif re.search('was the first time', entry['question'], re.I):
      if 'answer' in entry:
        ans[7] = entry['answer']

    elif re.search('The city you live', entry['question'], re.I):
      if 'answer' in entry:
        ans[8] = entry['answer']


  #return where, first_time, wechat_id, hobbies, books, company, position, first_attend, live_place
  return ans

def get_register_data(response, i, filename, event_name, count):
    dataEntry    = response.json()['attendees'][i]

    user_profile = dataEntry['profile']
    answers      = dataEntry['answers']
    status       = dataEntry['barcodes'][0]['status']
    est_time     = dataEntry['barcodes'][0]['created']

    utc_date = dateutil.parser.parse(est_time)
    date = utc_to_local(utc_date)

    if 'email' not in user_profile:
      user_profile['email']=''
    if not answers:
        return
    ans = findAnswers(answers)


    #print ans

    where= ans[0]
    first_time = ans[1]
    wechat_id = ans[2]
    hobbies = ans[3]
    books= ans[4]
    company = ans[5]
    position = ans[6]
    first_attend =ans[7]
    live_place = ans [8]

    if 'answer' in hobbies:
      hobbies_str = hobbies['answer'].replace(',', ' ').rstrip()
    else:
      hobbies_str = ''

    if 'answer' in first_attend:
      firstTime_str = first_attend['answer'].decode('utf-8')
    else:
      firstTime_str = ''

    name  = user_profile['name'].title()
    
    if 'email' in user_profile:
        email = user_profile['email'].lower()
    else:
        email = ''
    
    if not email:
        print '[Warning]The user %s do not provide an email address!\n' % (name)
        return 
    
    eventID = dataEntry['event_id']
    #status  = dataEntry['status']
    
    userRecord = collection.find_one({'email': email})
    
    if not userRecord:
      attended={}
      attended[event_name]=status
      id = collection.count() + 1
      first = event_name
         
      collection.insert({
               'name'    : name,
               'email'   : email,
               'wechatID': wechat_id,
               'company' : company,
               'job'     : position,
               'first'   : first,
               'hobby'   : hobbies,
               'books'   : books,
               'attended': attended,
               'ID'      : id,
               'city'    : live_place,
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
                               'wechatID' : wechat_id,
                               'hobby'  : hobbies,
                               'company' : company,
                               'job'     : position,
                               'books'   : books,
                               'attended': attended,
                               'city'    : live_place,
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

    '''if (collection.find({'email': user_profile['email']}).count() == 0) :
      collection.insert({
                       'name' : user_profile['name'],
                       'email': user_profile['email'],
                       'first time': firstTime_str,
                       'hobby': hobbies_str,
                       'Total attended': 1
                       })
    else:
      collection.update_one(
          {'email': user_profile['email']},
          {
            "$set" :  {'name' : user_profile['name'],
                       'email': user_profile['email'],
                       'first time': firstTime_str,
                       'hobby': hobbies_str,
                      },
            "$inc": {'Total attended': 1}
          }
      )'''


    i=i+50*count


    if (first_time == 'Yes'):
        if 'email' in user_profile:
            print i + 1, user_profile['name'].decode('utf-8'), user_profile['email'], wechat_id, first_time, \
                  '"' + hobbies.replace(',', ' ').rstrip() + '"', '"' + books.replace(',', ' ').rstrip() + '"', company, \
                  add_quote(position), add_quote(live_place), where, status, date
            str = '%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (i + 1, user_profile['name'].decode('utf-8'), user_profile['email'], wechat_id, first_time, \
                hobbies.replace(',', ' ').rstrip(), books.replace(',', ' ').rstrip(), company, position, \
                live_place, where, status, date)
        else:
            print i + 1, user_profile['name'].decode('utf-8'), wechat_id, first_time, \
                  '"' + hobbies.replace(',', ' ').rstrip() + '"', '"' + books.replace(',', ' ').rstrip() + '"', company, \
                  add_quote(position), add_quote(live_place), where, status, date
            str = '%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (i + 1, user_profile['name'].decode('utf-8'), wechat_id, first_time, \
                hobbies.replace(',', ' ').rstrip(), books.replace(',', ' ').rstrip(), company, position, \
                live_place, where, status, date)
    else :
        if 'email' in user_profile:
            print i + 1, user_profile['name'], user_profile['email'], first_time, add_quote(first_attend), where, status, date
            str = '%d,%s,%s.%s,%s,%s,%s,%s\n' % (i + 1, user_profile['name'], user_profile['email'], first_time, first_attend.decode('utf-8'), \
                 where, status, date)
        else:
            print i + 1, user_profile['name'], first_time, add_quote(first_attend), where, status, date
            str = '%d,%s,%s,%s,%s,%s,%s\n' % (i + 1, user_profile['name'], first_time, first_attend.decode('utf-8'), \
                 where, status, date)

    with open(filename, 'a') as  output_file:
        output_file.write(str)


"""def get_register_data(response, i, filename, event_name, flag):
    dataEntry    = response.json()['attendees'][i]
    
    user_profile = dataEntry['profile']
    answers      = dataEntry['answers']
    status       = dataEntry['barcodes'][0]['status']
    est_time     = dataEntry['barcodes'][0]['created']
    
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
"""

def get_all_members(response_eventm, end_count, first_page, count):

    if first_page:
        if response_event.json()["pagination"]["object_count"] >50:
            page_range = range(50)
        else:
            page_range = range(response_event.json()["pagination"]["object_count"])
    else:
        page_range = range(end_count)

    #print 'page_range is: ', page_range
    for j in page_range:
        #pass

        #comment for traverse all events
        #if j<response_event.json()["pagination"]["object_count"]-1 and notprintall:
        #    continue
        if first_page:
            print j+18, response_event.json()["events"][j]["name"]["text"]
        else:
            print j+50*count+18, response_event.json()["events"][j]["name"]["text"]
        #event_name = response_event.json()["events"][j]["name"]["text"]
        event_name = response_event.json()["events"][j]["name"]["text"].replace('.','')

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
            info =  '%s\n%d registered.\n' % (event_name.decode('utf-8'), object_count)
            with open(filename, 'a') as  output_file:
              output_file.write(info)
        else:
            object_count=0
            print 'nobody registered yet.'


        for i in range (object_count):
            if (i<50):
                get_register_data(response, i, filename, event_name, 0)

        if (object_count>50):
            for i in range(1, object_count/50+1):
            #print "https://www.eventbriteapi.com/v3/events/" + response_event.json()["events"][j]["id"] + "/attendees/?page="+str(i+1)

                response2 = requests.get(
                # "https://www.eventbriteapi.com/v3/users/me/owned_events/",
                    "https://www.eventbriteapi.com/v3/events/" + response_event.json()["events"][j]["id"] + "/attendees/?page="+str(i+1),
                    headers={
                    "Authorization": key,
                },
                verify=True,  # Verify SSL certificate
                )
                #print i
                for k in range((i)*50, (i+1)*50):
                    if k<object_count:
                      get_register_data(response2, k-50*i, filename, event_name, i)
    
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

object_count=response_event.json()["pagination"]["object_count"]
page_count = response_event.json()["pagination"]["page_count"]
#print response_event.json()["pagination"]["object_count"]

j = object_count%50-1
print 'First time is 18 %s' %(response_event.json()["events"][0]["name"]["text"])

lasttime=object_count+17

  #time=raw_input('Input the time you want:')

get_all_members(response_event, 0, 1, 1)

if page_count >1: 
    for i in range(1, page_count):
        #print 495, i, object_count
        response_event = requests.get(
        "https://www.eventbriteapi.com/v3/users/me/owned_events/?page="+str(i+1),
        headers={
            "Authorization": key,
        },
        verify=True,  # Verify SSL certificate
        )
        k=min((i+1)*50, object_count)
        get_all_members(response_event, k-50*i, 0, i)

#print 'last time is %d %s' %(lasttime, response_event.json()["events"][j]["name"]["text"])

# Get the attendees for each events. 

#get_all_members(response_event,0)
                
    #with open(filename, 'a+') as  output_file:
    #        output_file.write(response_event.json()["events"][j]["name"]["text"]+'\n')

