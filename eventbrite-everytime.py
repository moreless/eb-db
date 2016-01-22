#!/usr/bin/python
# coding: utf-8
import requests
import sys
import re
import calendar
import dateutil.parser
from datetime import datetime, timedelta

reload(sys)
sys.setdefaultencoding('utf-8')

def get_register_data(response, i, filename, flag):
	user_profile=response.json()['attendees'][i]['profile']
	answers = response.json()['attendees'][i]['answers']
	status= response.json()['attendees'][i]['barcodes'][0]['status']
	est_time = response.json()['attendees'][i]['barcodes'][0]['created']
	'''first_time=answers[3]
	wechat_id = answers[4]
	hobbies = answers[5]
	books = answers[6]
	company = answers[7]
	position = answers[8]
	first_attend =answers[9]
	live_place = answers[10]
	where = answers[1]'''
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

filename = 'guest.csv'

conf_file='eb.conf'
f = open(conf_file, 'r')
for key in f:
  key = key.rstrip()

response_event = requests.get(
    "https://www.eventbriteapi.com/v3/users/me/owned_events/",

    headers = {
        "Authorization": key,
    },
    verify = True,  # Verify SSL certificate
)
for j in range(response_event.json()["pagination"]["object_count"]):
	pass
	print response_event.json()["events"][j]["name"]["text"]

	#mo= re.findall(u'(第.+?期)', str(response_event.json()["events"][j]["name"]["text"]))
	#print mo[0]

	response = requests.get(
	    #"https://www.eventbriteapi.com/v3/users/me/owned_events/",
	    "https://www.eventbriteapi.com/v3/events/"+response_event.json()["events"][j]["id"]+"/attendees/",
	    headers = {
	        "Authorization": key,
	    },
	    verify = True,  # Verify SSL certificate
	)

	if (response.json()["pagination"]["object_count"]>50):
		response2 = requests.get(
		# "https://www.eventbriteapi.com/v3/users/me/owned_events/",
		"https://www.eventbriteapi.com/v3/events/" + response_event.json()["events"][j]["id"] + "/attendees/?page=2",
		headers={
		    "Authorization": key,
		},
		verify=True,  # Verify SSL certificate
		)
			
	with open(filename, 'a+') as  output_file:
				output_file.write(response_event.json()["events"][j]["name"]["text"]+'\n')

	'''for i in range (response.json()["pagination"]["object_count"]):
		user_profile=response.json()['attendees'][i]['profile']
		answers = response.json()['attendees'][i]['answers']
		status= response.json()['attendees'][i]['barcodes'][0]['status']
		est_time = response.json()['attendees'][i]['barcodes'][0]['created']
		first_time=answers[2]
		wechat_id = answers[3]
		hobbies = answers[4]
		books = answers[5]
		company = answers[6]
		position = answers[7]
		first_attend =answers[8]
		live_place = answers[9]
		where = answers[10]
		utc_date = dateutil.parser.parse(est_time)
		date = utc_to_local(utc_date)

		try :
			wechat_id['answer']
			hobbies['answer']
			print i+1, user_profile['name'].decode('utf-8'), user_profile['email'], wechat_id['answer'], first_time['answer'], \
			      '"'+hobbies['answer'].replace(',', ' ').rstrip()+'"', '"'+books['answer'].replace(',', ' ').rstrip()+'"', company['answer'], \
			      add_quote(position['answer']), add_quote(live_place['answer']), where['answer'], status, date
			str='%d,%s,%s.%s,%s\n' %(i+1, user_profile['name'], user_profile['email'], wechat_id['answer'], hobbies['answer'])
		except :
			print i+1, user_profile['name'], user_profile['email'], first_time['answer'], add_quote(first_attend['answer']), status, date
			str='%d,%s,%s\n' % (i+1, user_profile['name'], user_profile['email'])'''
	for i in range (response.json()["pagination"]["object_count"]):
		if (i<50):
			get_register_data(response, i, filename, False)
		else:
			get_register_data(response2, i-50, filename, True)
