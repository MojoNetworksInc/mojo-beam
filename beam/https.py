import json
import requests
import sys
from django.conf import settings
from beam.models import configuration

VERIFY = False
HEADERS = {'content-type': 'application/json'}
CONNECTION_TIMEOUT = 60
DEFAULT_CUSTOMER_ID="ATN4"

def mwm_login(url, exposedCustomerId):
	loginUrlPath = url + settings.MWM_LOGIN_PATH	
	payload = json.dumps({"type":"apikeycredentials","keyId": get_kvs_key(),"keyValue": get_kvs_key_value(),"exposedCustomerId": exposedCustomerId})
	try:
		response = requests.post(loginUrlPath, data = payload, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		return response
	except requests.exceptions.RequestException as e:
		print "error in fetching locations", e
		raise e		

def fetch_location_tree(url):
	exposedCustomerId = get_customer_id()
	response = mwm_login(url, exposedCustomerId)		
	try:
		locationPath=url+ settings.MWM_LOCATION_TREE 
		response = requests.get(locationPath, cookies =response.cookies,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		if response.status_code == requests.codes.ok:
			response_json = response.json()			
			locations = response_json["locations"]
			#print locations
			return locations
		else:
			print("Unrecognised status for fetching services available for customer" + str(response.status_code))
			return None
	except requests.exceptions.RequestException as e:
		print e
		return None

def get_kvs_key():	
	key_name = settings.KEY_NAME	
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:						
			if o.key_name==settings.KEY_NAME_KEY:
				key_name = o.key_value
	return key_name

def get_kvs_key_value():	
	key_value = settings.KEY_VALUE	
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:						
			if o.key_name==settings.KEY_NAME_VALUE:
				key_value = o.key_value
	return key_value
			

def get_mlp_url():
	mlp_url = settings.MLP_URL
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:			
			if o.key_name==settings.MLP_URL_KEY:
				mlp_url = o.key_value		
	return mlp_url



def mlp_Login():
	mlp_url = settings.MLP_URL
	key_name = settings.KEY_NAME
	key_value = settings.KEY_VALUE
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:
			print o
			if o.key_name==settings.MLP_URL_KEY:
				mlp_url = o.key_value
			if o.key_name==settings.KEY_NAME_KEY:
				key_name = o.key_value
			if o.key_name==settings.KEY_NAME_VALUE:
				key_value = o.key_value
	
	
	mlp_url = mlp_url +settings.MLP_LOGIN_PATH.format(key_name,key_value)

	#print "MLP URL", mlp_url
	try:
		return requests.get(mlp_url, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
	except requests.exceptions.RequestException as e:
		raise e
		
def get_customer_id():
	exposedCustomerId = DEFAULT_CUSTOMER_ID
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:
			if o.key_name==settings.CUSTOMER_ID:
				exposedCustomerId = o.key_value
	return exposedCustomerId


def getServices():	
	response = mlp_Login()	

	print response.cookies
	#print "login to MLP successfull"
	exposedCustomerId = get_customer_id()		
	#print "exposedCustomerId ", exposedCustomerId
	service_url = None	
	try:
		get_services_url = get_mlp_url() + settings.MLP_GET_MWM_SERVICES_FOR_CUSTOMER.format(exposedCustomerId)
		print get_services_url
		response = requests.get(get_services_url, cookies=response.cookies, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		json_reponse = response.json()
		#print json_reponse
		data = json_reponse["data"]
		print data
		services = data["customerServices"]
		for e in services:
			service = e["service"]
			#print service
			service_url = service["service_url"]
		return service_url							
	except requests.exceptions.RequestException as e:
		print e
		return None

def get_device_templates():
	service = https.getServices()
	split = service.split("?CID=")
	#print split[0], get_customer_id()

if __name__ == '__main__':
    print("This only executes when  is executed rather than imported")
    get_device_templates()


	






	

