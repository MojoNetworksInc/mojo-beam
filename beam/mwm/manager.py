import os
import sys
import json
import requests
import urllib
from django.conf import settings
from beam.models import configuration


VERIFY = False
HEADERS = {'content-type': 'application/json'}
CONNECTION_TIMEOUT = 60

DEFAULT_CUSTOMER_ID=settings.DEFAULT_CUSTOMER_ID

DEFAULT_LOCATION_ID=1
DEFAULT_lOCATION = '{"type":"locallocationid", "id":"{}"}'

def mwm_login(url, exposedCustomerId):
	loginUrlPath = url + settings.MWM_LOGIN_PATH
	print "loginUrlPath", loginUrlPath
	payload = json.dumps({"type":"apikeycredentials","keyId": get_kvs_key(),"keyValue": get_kvs_key_value(),"exposedCustomerId": exposedCustomerId})
	try:
		response = requests.post(loginUrlPath, data = payload, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)		
		return response
	except requests.exceptions.RequestException as e:
		print e
		return None

def fetch_location_tree(url, exposedCustomerId):
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

def mlp_Login():			
	local_url = get_mlp_url() + settings.MLP_LOGIN_PATH.format(get_kvs_key(),get_kvs_key_value())
	print local_url
	try:
		return requests.get(local_url, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
	except requests.exceptions.RequestException as e:
		print e
		return None


def get_customer_id():
	exposedCustomerId = DEFAULT_CUSTOMER_ID
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:
			if o.key_name==settings.CUSTOMER_ID:
				exposedCustomerId = o.key_value
	return exposedCustomerId			

def get_mlp_url():
	mlp_url = settings.MLP_URL
	if settings.IS_PRODUCTION:
		objects = configuration.objects.all()
		for o in objects:			
			if o.key_name==settings.MLP_URL_KEY:
				mlp_url = o.key_value		
	return mlp_url		



def getServices():	

	response = mlp_Login()	
	print "get services"
	exposedCustomerId = get_customer_id()
	service_url = None	
	try:
		get_services_url = get_mlp_url()+ settings.MLP_GET_MWM_SERVICES_FOR_CUSTOMER.format(exposedCustomerId)
		print get_services_url
		#print get_services_url
		response = requests.get(get_services_url, cookies=response.cookies, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)						
		json_reponse = response.json()
		
		#print json_reponse
		data = json_reponse["data"]
		services = data["customerServices"]
		for e in services:
			service = e["service"]
			#print service
			service_url = service["service_url"]
		return service_url							
	except requests.exceptions.RequestException as e:
		print e
		return None

def login_cookies():
	service = getServices()	
	split = service.split("?CID=")
	#print split[0]
	response = mwm_login(split[0], get_customer_id())
	return split[0], get_customer_id() ,response.cookies


def get_system_default_ssid(mwm_url, mwm_cookies):
	try:				
		get_services_url = mwm_url+ settings.GET_DEFAULT_SSID.format(0)	
		response = requests.get(get_services_url, cookies=mwm_cookies, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		json = response.json()				
		return json

	except requests.exceptions.RequestException as e:
		print e
		return None


def get_all_ssid_profiles(data):	
	if data is None:
		data = login_cookies()
	print data[0], data[1], data[2]
	mwm_bse_url = data[0]
	cookies_ = data[2]
	try:				
		get_services_url = mwm_bse_url+ settings.GET_ALL_SSID_PROFILE.format(DEFAULT_LOCATION_ID)	
		print get_services_url			
		response = requests.get(get_services_url, cookies=cookies_, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		json_reponse = response.json()

		for j in json_reponse:
			print "-----------"
			print json.dumps(j)
			print "-----------"
		return json_reponse						
	except requests.exceptions.RequestException as e:
		print e
		return None


def update_device_template_with_ssid(mwm_url, location_id, request_body, mwm_coookies ):					
	try:
		get_services_url = mwm_url+ settings.CREATE_TEMPLATE_DETAILS.format(location_id)
		response = requests.post(get_services_url, data = request_body, cookies=mwm_coookies, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)
		#print "update ", response
		return response
	except requests.exceptions.RequestException as e:
		print e
		raise e


def get_template_details(mwm_bse_url, cookies_, template_id, location_id):
	try:
		get_services_url = mwm_bse_url+ settings.GET_TEMPLATE_DETAILS.format(template_id, location_id)
		print get_services_url
		#print get_services_url
		response = requests.get(get_services_url, cookies=cookies_, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		print "get_template_details response", response
		json_reponse = response.json()
		return json_reponse
	except requests.exceptions.RequestException as e:
		print e
		return None

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def is_inheritied(mwm_bse_url, location_id, cookies_):	
	applied_device_url = mwm_bse_url + settings.GET_MWM_DEVICE_TEMPLATE_APPLIED.format(location_id)
	print "is_inheritied ", applied_device_url
	try:
		response = requests.get(applied_device_url, cookies=cookies_,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		print response
		if response.status_code == requests.codes.ok:
			response_json = response.json()	
			configuration_policy = response_json
			policyCreatedAtLocId = configuration_policy["policyCreatedAtLocId"]
			value =  byteify(policyCreatedAtLocId)
			locationLocationId = value["id"]
			if locationLocationId == location_id:
				return False
			else:
				return True
		else:
			print("Unrecognised status for fetching services available for customer" + str(response.status_code))
			return False
	except requests.exceptions.RequestException as e:
		print e
		return None

def delete_ssid_profile(ssid_request_obj):
	print "going to fetch device template now"
	device_template = get_applied_device_template(ssid_request_obj)
	
	service = getServices()
	split = service.split("?CID=")
	mwm_url = split[0]		
	response = mwm_login(split[0], get_customer_id())	
	cookies_=response.cookies		
	profiles= []
	if device_template:	
		ssid_profiles = device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["ssidProfiles"]		
		print "ssidProfiles# ", len(ssid_profiles)
		request_name = ssid_request_obj.ssid_name
		location_id = ssid_request_obj.location_id
		#print "number of profiles ", len(ssid_profiles)
		for sp in ssid_profiles:			
			value= byteify(sp)
		#	print "---" , value, "---"					
			ssid_name = value["ssid"]
			if ssid_name != request_name:
				profiles.append(sp)
		value_to_pass = profiles
		#print value_to_pass
		print "len(profiles#)" , len(profiles)
		if len(profiles) > 0:
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["configured"]=True
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["configured"]=True
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["3"]["configured"]=True
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["ssidProfiles"]=[]
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["ssidProfiles"]=[]

			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["ssidProfiles"] =[]
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["ssidProfiles"] =[]
			
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["configured"]=True
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["configured"]=True
			print "len(value_to_pass#)" , len(value_to_pass)
			for v in value_to_pass:
				device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["ssidProfiles"].append(v)
				device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["ssidProfiles"].append(v)
				device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["ssidProfiles"].append(v)
				device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["ssidProfiles"].append(v)			
			
			try:
				#print "updating 1", json.dumps(device_template)
				response = update_device_template_with_ssid(mwm_url, location_id, json.dumps(device_template), cookies_)
				if response.status_code == requests.codes.ok:
					return response.json()
				print "error received", response.status_code
				return None
			except Exception as e:				
				raise e						
		else:
			# this is last profile therefore we need to remove ssid profile wrapper
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["configured"]=True
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["configured"]=True
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["3"]["configured"]=True
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["ssidProfiles"] =[]
			device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["ssidProfiles"]=[]
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["configured"]=True
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["configured"]=True
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["ssidProfiles"]=[]
			device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["ssidProfiles"]=[]
			try:
				print "updating 2"
				response = update_device_template_with_ssid(mwm_url, location_id, json.dumps(device_template), cookies_)
				if response.status_code == requests.codes.ok:
					return response.json()
				print "error received", response.status_code
				return None
			except Exception as e:				
				raise e					
	return None


def get_applied_device_template(ssid_request_obj):
	location_id = ssid_request_obj.location_id
	ssid_name = ssid_request_obj.ssid_name		
	service = getServices()
	split = service.split("?CID=")
	print split[0]
	mwm_url = split[0]		
	response = mwm_login(split[0], get_customer_id())	
	cookies_=response.cookies	
	applied_device_url = split[0] + settings.GET_MWM_DEVICE_TEMPLATE_APPLIED.format(location_id)
	configuration_policy =None
	try:	
		default_template_id	= -2
		created_at_location = 0		
		response = requests.get(applied_device_url, cookies=cookies_,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		print "get_applied_device_template resonse -->", response
		if response.status_code == requests.codes.ok:
			response_json = response.json()	
			configuration_policy = response_json	
			#print response_json	
			applied_template_id = response_json["defaultTemplateId"]
			created_at_location =response_json["policyCreatedAtLocId"]["id"]
			print "Going to get template ", applied_template_id, " Details on location ID ", location_id
			template_details = get_template_details(mwm_url,cookies_, applied_template_id, location_id )	
			print "template_details ", template_details
			return template_details
		else:
			print("Unrecognised status for fetching services available for customer" + str(response.status_code))
			return None
								
	except requests.exceptions.RequestException as e:
		print e
		return None


def get_device_templates(ssid_location_id):
	service = getServices()
	split = service.split("?CID=")	
	mwm_url = split[0]		
	response = mwm_login(split[0], get_customer_id())	
	cookies_=response.cookies	
	applied_device_url = split[0] + settings.GET_MWM_DEVICE_TEMPLATE_APPLIED.format(ssid_location_id)
	configuration_policy =None
	try:	
		default_template_id	= -2
		created_at_location = 0		
		response = requests.get(applied_device_url, cookies=cookies_,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		if response.status_code == requests.codes.ok:
			response_json = response.json()	
			#configuration_policy = response_json	
			print response_json	
			#applied_template_id = response_json["defaultTemplateId"]
			#created_at_location =response_json["policyCreatedAtLocId"]["id"]						
			#print "hello"
			return response_json
		else:
			print("Unrecognised status for fetching services available for customer" + str(response.status_code))		
	except requests.exceptions.RequestException as e:
		print e
		return None
	return None

def get_all_templates():
	templates = None
	applied_template = None
	system_template = None
	another_template = None
	all_templates_url = split[0] + settings.GET_MWM_DEVICE_TEMPLATES.format(ssid_location_id)
	response = requests.get(all_templates_url, cookies=cookies_,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
	if response.status_code == requests.codes.ok:
		response_json = response.json()		
		templates = response_json	
		for r in response_json:
			template_id =  r["templateId"]
			print "template_id", template_id
			if template_id == applied_template_id:
					#print "applied template", json.dumps(r)
				applied_template =r			
				print "applied template id", template_id	
			if template_id == -2:
				print "system template"
				system_template = r
			if template_id == -1:
				print "another template"
				another_template = r

		if given_location == created_at_location:
			print "Customize"
				# in this case get customize template and add the ssid profile
		else:
			print "Inhertied" 
	return templates
				
				

def create_device_template(mwm_url,template_name , location_id, mwm_cookies):	
	default_tempalte_response = get_template_details(mwm_url, mwm_cookies, -2, location_id)	
	default_tempalte_response["sensorPassword"] = "config"
	default_tempalte_response["templateName"] = template_name			
	try:
		get_services_url = mwm_url+ settings.CREATE_TEMPLATE_DETAILS.format(location_id)
		response = requests.put(get_services_url, data = json.dumps(default_tempalte_response), cookies=mwm_cookies, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		res_json= response.json()
		print res_json
		return res_json
	except requests.exceptions.RequestException as e:
		raise e

def create_ssid(mwm_url, mwm_cookies, ssid_request_obj):		
	#print "ssid ", ssid_name	
	ssid_name = ssid_request_obj.ssid_name
	location_id = ssid_request_obj.location_id

	default_ssid = get_system_default_ssid(mwm_url, mwm_cookies)
	default_ssid["ssid"]=ssid_name
	default_ssid["templateName"]=ssid_name
	wirelessProfile = default_ssid["wirelessProfile"]
		
	
	

	print "secutrity",  ssid_request_obj.security
	print "password",  ssid_request_obj.password
	
	'''
	apSecurityMode
		0 for open  --> o
		1 for WEP ---> Not supported by beam as of now
		3 for WPA2 --> 1
		4 for WPA/WPA2 mixed --> 2

	Type of security mode. The applicable values are:
		open
		wep
		wpa2
		wpa2Mixed
		osen

	authtype
		PSK
		EAP
	
	'''
	securityMode = wirelessProfile["securityMode"]

	if ssid_request_obj.security ==0:
		securityMode["type"]="open"
		wirelessProfile["apSecurityMode"]=0		
	if ssid_request_obj.security ==1:
		securityMode["type"]="wpa2"
		wirelessProfile["apSecurityMode"]=3
		securityMode["authType"]="PSK"
		securityMode["pskPassphrase"]=ssid_request_obj.password
	if ssid_request_obj.security ==2:
		securityMode["type"]="wpa2Mixed"
		wirelessProfile["apSecurityMode"]=4
		securityMode["authType"]="PSK"
		securityMode["pskPassphrase"]=ssid_request_obj.password
	

	wirelessProfile["securityMode"] = securityMode
	default_ssid["wirelessProfile"] = wirelessProfile 

	request_body= json.dumps(default_ssid)
	
	try:				
		get_services_url = mwm_url+ CREATE_SSID.format(location_id)	
		response = requests.put(get_services_url, data=request_body,  cookies=mwm_cookies, verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)						
		#print response.json()
		return response.json()					
	except requests.exceptions.RequestException as e:
		print e
		return None

'''
This method will create 
	new ssid on MWM service
	update the applied device tempalate with created ssid
'''
def create_and_add_ssid_profile(device_template , mwm_url,  mwm_cookies, ssid_request_obj):
	ssid_name = ssid_request_obj.ssid_name
	location_id = ssid_request_obj.location_id
	ssid_profiles = create_ssid(mwm_url, mwm_cookies, ssid_request_obj )
	device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["configured"]=True
	device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["configured"]=True
	device_template["modelAgnosticRadioIdToRadioSettingsMap"]["3"]["configured"]=True
	device_template["modelAgnosticRadioIdToRadioSettingsMap"]["1"]["ssidProfiles"].append(ssid_profiles)
	device_template["modelAgnosticRadioIdToRadioSettingsMap"]["2"]["ssidProfiles"].append(ssid_profiles)
	
	device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["configured"]=True
	device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["configured"]=True
	device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][0]["ssidProfiles"].append(ssid_profiles)
	device_template["platformToRadioSettingsMapper"]["platformToRadioSettingsMap"]["1000"][1]["ssidProfiles"].append(ssid_profiles)

	data = update_device_template_with_ssid(mwm_url, location_id, json.dumps(device_template), mwm_cookies)
	return device_template	

'''
This method will create 
	New device template
	New ssid on MWM service
	Add ssid in device template and update the device template
'''
def create_device_template_and_assign_ssid(mwm_url, device_template_name , mwm_cookies, ssid_request_obj):
	ssid_name = ssid_request_obj.ssid_name
	location_id = ssid_request_obj.location_id
	device_template = create_device_template(mwm_url, device_template_name, location_id, mwm_cookies)
	return create_and_add_ssid_profile(device_template, mwm_url, mwm_cookies , ssid_request_obj )


def customize_policy_at_location(mwm_url, location_id, mwm_cookies):	
	applied_device_url = mwm_url + settings.MWM_DEVICE_TEMPLATE_APPLIED.format(location_id)
	try:								
		print "customize_policy_at_location url ",applied_device_url
		response = requests.put(applied_device_url, cookies=mwm_cookies,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		if response.status_code == requests.codes.no_content:			
			return True		
		else:
			if response.status_code == requests.codes.bad_request:
				error_response=response.json()
				print "error error_response " ,error_response
				errors =error_response["errors"]
				for e in errors:					
					if e["errorCode"]=="-18":						
						return True
					else:
						print "Customize device config: Unrecognised status for customer: HTTP code " + str(response.status_code)		
		return None
	except requests.exceptions.RequestException as e:
		print e
		return None

def inherit_policy_at_location(mwm_url, location_id, mwm_cookies):	
	applied_device_url = mwm_url + settings.MWM_DEVICE_TEMPLATE_APPLIED.format(location_id)
	try:								
		response = requests.delete(applied_device_url, cookies=mwm_cookies,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		if response.status_code == requests.codes.no_content:			
			return True		
		else:
			if response.status_code == requests.codes.bad_request:
				error_response=response.json()
				errors =error_response["errors"]
				for e in errors:					
					if e["errorCode"]=="-18":						
						return True
					else:
						print "Inherit device config: Unrecognised status for customer: HTTP code " + str(response.status_code)		
		return None
	except requests.exceptions.RequestException as e:
		print e
		return None


def mark_default_device_tempalate(mwm_url, location_id, template_id, mwm_cookies):		
	
	try:					
			
		#response = requests.put(applied_device_url, cookies=mwm_cookies,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		#if response.status_code == requests.codes.ok:
		#	response_json = response.json()					
		#else:
		#	print("Customize device config: Unrecognised status for customer: HTTP code " + str(response.status_code))
		#	return None			
		
		device_confi_url = mwm_url + settings.GET_MWM_DEVICE_TEMPLATE_APPLIED.format(location_id)
		configuration_response = requests.get(device_confi_url, cookies=mwm_cookies,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				

		data = configuration_response.json()

		#data = configuration_response.json()
		data["policyCreatedAtLocId"]["id"] = location_id
		data["defaultTemplateId"]=template_id
		data["applyToExistingDevices"]=True
		applied_device_url = mwm_url + MWM_DEVICE_TEMPLATE_APPLIED.format(location_id)
		response = requests.post(applied_device_url,data=json.dumps(data), cookies=mwm_cookies,  verify=VERIFY, headers = HEADERS, timeout = CONNECTION_TIMEOUT)				
		if response.status_code == requests.codes.no_content:
			return True			
		else:
			if response.status_code == requests.codes.bad_request:
				error_response=response.json()
				errors =error_response["errors"]
				for e in errors:					
					print e
			print("Mark default: Unrecognised status for customer: HTTP code: " + str(response.status_code))
			return None
	except requests.exceptions.RequestException as e:
		print e
		return None		

class Manager:
	location_id=None
	mwm_url=None
	cookies_=None

	def __init__(self, location_id):
		self.location_id = location_id

	def login(self):
			service = getServices()
			split = service.split("?CID=")
			self.mwm_url = split[0]
			response = mwm_login(split[0], split[1])
			self.cookies_=response.cookies
	def get_mwmURL(self):
		return self.mwm_url

	def get_cookies_(self):
		return self.cookies_


def delete_ssid_from_device_template(ssid_request_obj):
	location_id = ssid_request_obj.location_id
	ssid_name = ssid_request_obj.ssid_name
	try:
		service = getServices()
		split = service.split("?CID=")
		print split[0]
		mwm_url = split[0]
		response = mwm_login(split[0], get_customer_id())
		cookies_=response.cookies

		inherited =  is_inheritied(mwm_url,  ssid_location_id, cookies_)
	# on given location, check policy is inherited or not
	#print inherited
		if inherited:
			print "policy is inherited"			
		# if policy is inherited then we need to customize it
			succes = customize_policy_at_location(mwm_url, ssid_location_id, cookies_)
			if succes:
				print "customized policy on given location"
				print "creating device template and assigning ssid"
				device_template = create_device_template_and_assign_ssid(mwm_url , "mojo beam", cookies_, ssid_request_obj)			
				mark_default_device_tempalate(mwm_url, ssid_location_id, device_template["templateId"], cookies_)
				return True
		else:	
			print "policy is customized"
	except Exception as e:
		return False
	# if nothing works, return false			
	return False


def approve_and_create_ssid(ssid_request_obj):
	location_id = ssid_request_obj.location_id
	ssid_name = ssid_request_obj.ssid_name
	return approve_ssid(ssid_request_obj, location_id, ssid_name)


def approve_ssid(ssid_request_obj, ssid_location_id, ssid_name):
	split = None
	try:
		service = getServices()
		#print "inside approve ssid1 ", service
		try:
			split = service.split("?CID=")
		except Exception as e:
			print e
			raise e		
		#print "split value", split
		print "MWM URL ",split[0]
		mwm_url = split[0]
		response = mwm_login(split[0], get_customer_id())
		cookies_=response.cookies
		print cookies_
		inherited =  is_inheritied(mwm_url,  ssid_location_id, cookies_)
	# on given location, check policy is inherited or not
	#print inherited
		if inherited:
			print "policy is inherited"
		# if policy is inherited then we need to customize it
			succes = customize_policy_at_location(mwm_url, ssid_location_id, cookies_)
			if succes:
				print "customized policy on given location"
				print "creating device template and assigning ssid"
				device_template = create_device_template_and_assign_ssid(mwm_url , "mojo beam", cookies_, ssid_request_obj)			
				mark_default_device_tempalate(mwm_url, ssid_location_id, device_template["templateId"], cookies_)
				return True
		else:	
			print "policy is not inherited"
			# get all device template on the given location
			applied_device_template = get_applied_device_template(ssid_request_obj)
			# need to check if ssid profile already existing [Not implemented]
			# 1. Create a new ssid and append it to existing device template
			# 2. Update device template
			
			updated_template = create_and_add_ssid_profile(applied_device_template, mwm_url, cookies_, ssid_request_obj)			
			if updated_template:
				return True
			return False
	except Exception as e:
		return False
	# if nothing works, return false			
	return False			
	  

if __name__ == '__main__': 
	manager = Manager(0)
	
	try:
		#manager.login()
		#print manager.get_mwmURL()
		#print manager.get_cookies_()
		approve_ssid(DEFAULT_LOCATION_ID,  "hero")
	
	except Exception as e:
		raise
	else:
		pass
	finally:
		pass
	



    





	






	

