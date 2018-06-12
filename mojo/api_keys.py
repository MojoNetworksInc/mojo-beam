# reference keys  
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# custome defined keys, pls do not change it
MLP_URL_KEY="MLP_URL"
KEY_NAME_KEY="KVS_KEY"
KEY_NAME_VALUE="KVS_VALUE"
CUSTOMER_ID="CUSTOMER_ID"



# You need to request mojo for the following values:
MLP_URL="https://xxx.com"
KEY_NAME="KEY-XXX"
KEY_VALUE="XXXXXX" 
DEFAULT_CUSTOMER_ID = "XXXX"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}



MWM_LOGIN_PATH = "/new/webservice/login/key/KEY_LOGIN/300"
MLP_LOGIN_PATH = "/rest/api/v2/kvs/login?key_id={}&key_value={}&session_timeout=60"
MLP_GET_MWM_SERVICES_FOR_CUSTOMER = "/rest/api/v2/customers/{}/services?type=amc"
MWM_DEVICE_TEMPLATE="/new/webservice/V3/templates/DEVICE_TEMPLATE?locationid={}&minimalinforequired=true"
MWM_LOCATION_TREE="/new/webservice/v2/locations/tree"
GET_MWM_DEVICE_TEMPLATES="/new/webservice/V5/templates/DEVICE_TEMPLATE?locationid={}&modelspecific=true&nodeid=0"
MWM_DEVICE_TEMPLATE_APPLIED="/new/webservice/v5/policies/deviceconfig/?locationid={}"
GET_MWM_DEVICE_TEMPLATE_APPLIED="/new/webservice/v5/policies/deviceconfig/false?locationid={}"
MARK_DEFAULT_TEMPLATE_ID="/new/webservice/v5/policies/deviceconfig?locationid={}"
GET_TEMPLATE_DETAILS="/new/webservice/v5/configuration/devicetemplates/{}?modelspecific=true&locationid={}&nodeid=0"
CREATE_TEMPLATE_DETAILS="/new/webservice/v5/configuration/devicetemplates/?modelspecific=true&locationid={}&nodeid=0"
GET_ALL_SSID_PROFILE="/new/webservice/v5/configuration/ssidprofiles?nodeid=0&locationid={}"
GET_DEFAULT_SSID="/new/webservice/v5/configuration/ssidprofiles/-1?locationid={}&nodeid=0"
CREATE_SSID="/new/webservice/v5/configuration/ssidprofiles?locationid={}&nodeid=0"
MWM_LOCATION_TREE="/new/webservice/v2/locations/tree"