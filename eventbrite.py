#!/usr/local/bin/python
# coding: utf-8
import requests
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

filename = 'output.csv'

response_event = requests.get(
    "https://www.eventbriteapi.com/v3/users/me/owned_events/",

    headers = {
        "Authorization": "Bearer 76IZEIMV6O2VAOYUCKOE",
    },
    verify = True,  # Verify SSL certificate
)
for j in range(response_event.json()["pagination"]["object_count"]):
	print response_event.json()["events"][j]["name"]["text"]

	#mo= re.findall(u'(第.+?期)', str(response_event.json()["events"][j]["name"]["text"]))
	#print mo[0]

response = requests.get(
    #"https://www.eventbriteapi.com/v3/users/me/owned_events/",
    "https://www.eventbriteapi.com/v3/events/"+response_event.json()["events"][j]["id"]+"/attendees/",
    headers = {
        "Authorization": "Bearer 76IZEIMV6O2VAOYUCKOE",
    },
    verify = True,  # Verify SSL certificate
)
		
'''with open(filename, 'a+') as  output_file:
			output_file.write(response_event.json()["events"][j]["name"]["text"]+'\n')'''

for i in range (response.json()["pagination"]["object_count"]):
	user_profile=response.json()['attendees'][i]['profile']
	wechat_id=response.json()['attendees'][i]['answers'][5]
	hobbies=response.json()['attendees'][i]['answers'][3]
	try :
		wechat_id['answer']
		hobbies['answer']
		user_profile['email']
		print i+1, user_profile['name'], user_profile['email'], wechat_id['answer'], hobbies['answer']
		str='%d,%s,%s.%s,%s\n' %(i+1, user_profile['name'], user_profile['email'], wechat_id['answer'], hobbies['answer'])
	except :
		try :
			user_profile['email']
			print i+1, user_profile['name'], user_profile['email']
			str='%d,%s,%s\n' % (i+1, user_profile['name'], user_profile['email'])
		except:
			print i+1, user_profile['name']
			str='%d,%s\n' %(i+1, user_profile['name'])

	'''with open(filename, 'a+') as  output_file:
			output_file.write(str)'''