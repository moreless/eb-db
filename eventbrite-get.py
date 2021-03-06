#!/usr/bin/python
# coding: utf-8

import requests
import sys, time
import re
import calendar
import dateutil.parser
from datetime import datetime, timedelta
import urllib3
urllib3.disable_warnings()

#import pymongo
#from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('utf-8')

def findAnswers(answers):
  ans=['','','','','','','','','']
  '''
    This funciton is used to find the wechatID, hobby, company and job.
  '''

  if not answers:
    print 'Errors! No answers found in this entry.'
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

def get_register_data(response, i, filename, count):
    dataEntry    = response.json()['attendees'][i]

    user_profile = dataEntry['profile']
    if 'email' not in user_profile:
      user_profile['email']=''
    answers      = dataEntry['answers']
    ticket_class = dataEntry["ticket_class_name"]
    status       = dataEntry['barcodes'][0]['status']
    est_time     = dataEntry['barcodes'][0]['created']
    cost         = dataEntry['costs']['gross']['display']

    utc_date = dateutil.parser.parse(est_time)
    date = utc_to_local(utc_date)

    if not answers:
        address = user_profile['addresses']
        i=i+50*count
        if address != {} and 'address_1' in user_profile['addresses']['bill']:
          print i+1, user_profile['name'], user_profile['email'], user_profile['company'], user_profile['job_title'], \
              '"'+address['bill']['address_1']+',', address['bill']['city'], address['bill']['postal_code']+'"', \
              status, '"'+ticket_class+'"', cost, date
        else:
          print i+1, user_profile['name'], user_profile['email'], user_profile['company'], user_profile['job_title'], \
              status, '"'+ticket_class+'"', cost, date
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
        print i + 1, user_profile['name'].decode('utf-8'), user_profile['email'], wechat_id, first_time, \
              '"' + hobbies.replace(',', ' ').rstrip() + '"', '"' + books.replace(',', ' ').rstrip() + '"', company, \
              add_quote(position), add_quote(live_place), where, status, '"'+ticket_class+'"', cost, date
        str = '%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (i + 1, user_profile['name'].decode('utf-8'), user_profile['email'], wechat_id, first_time, \
            hobbies.replace(',', ' ').rstrip(), books.replace(',', ' ').rstrip(), company, position, \
            live_place, where, status, '"'+ticket_class+'"', cost, date)
    else :
        print i + 1, user_profile['name'], user_profile['email'], first_time, add_quote(first_attend), where, status, '"'+ticket_class+'"', cost, date
        str = '%d,%s,%s.%s,%s,%s,%s,%s,%s,%s\n' % (i + 1, user_profile['name'], user_profile['email'], first_time, first_attend.decode('utf-8'), \
         where, status, '"'+ticket_class+'"', cost, date)

    with open(filename, 'a') as  output_file:
        output_file.write(str)


def utc_to_local(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def add_quote(str):
    return '"' + str + '"'

if __name__== "__main__":

  filename = 'output.csv'

  user = range(3)
  conf_file='eb.conf'

  f = open(conf_file, 'r')
  for line in f: 
    line = line.rstrip()
    user = line.split(', ')
    key = user[0]


  response_event = requests.get(
      "https://www.eventbriteapi.com/v3/users/me/owned_events/",

      headers={
          "Authorization": key,
      },
      verify=True,  # Verify SSL certificate
  )

  object_count=response_event.json()["pagination"]["object_count"]
  page_count = response_event.json()["pagination"]["page_count"]
  
  print "object_count is %d, page_count is %d" % ( object_count, page_count)
  #object_count = 250
  #page_count = 5
  j = (object_count)%50-1

  print 'First time is 18', response_event.json()["events"][0]["name"]["text"].decode('utf-8')

  lasttime=object_count+17

  if page_count >1: 
    response_event = requests.get(
        "https://www.eventbriteapi.com/v3/users/me/owned_events/?page="+str(page_count),
        headers={
            "Authorization": key,
        },
        verify=True,  # Verify SSL certificate
    )
  print 'last time is %d ' %(lasttime), response_event.json()["events"][j]["name"]["text"].decode('utf-8')
  #time=raw_input('Input the time you want:')

  #j = int(time)-18

  for i in range(j, j-10, -1):
    print response_event.json()["events"][i]["name"]["text"]
    print 'event_id', response_event.json()["events"][i]["id"]

    event_name = response_event.json()["events"][i]["name"]["text"]
    # mo= re.findall(u'(第.+?期)', str(response_event.json()["events"][j]["name"]["text"]))
    # print mo[0]

    response = requests.get(
        # "https://www.eventbriteapi.com/v3/users/me/owned_events/",
        "https://www.eventbriteapi.com/v3/events/" + response_event.json()["events"][i]["id"] + "/attendees/",
        headers={
            "Authorization": key,
        },
        verify=True,  # Verify SSL certificate
    )

    if 'object_count' in response.json()["pagination"]:
      object_count= response.json()["pagination"]["object_count"]
      print object_count, "registered\n"
    else:
      object_count=0
      print 'nobody registered yet.'
    info =  '%s\n%d registered.\n' % (event_name, object_count)
  

  #with open(filename, 'a') as  output_file:
   #           output_file.write(response_event.json()["events"][j]["name"]["text"] + '\n')
  str= (time.strftime('%H:%M:%S %m/%d/%Y'))
  print '\nQuery at time: '+str
