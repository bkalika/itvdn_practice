import json

import requests
from flask.json import dumps
from requests.auth import HTTPBasicAuth


PORTAL_LOGIN = 'cssp_system'
PORTAL_PASSWORD = '!Cth_w3y4k'

get_general_info_url = "http://10.10.16.248:8888/portal-service/loyal/getGeneralInfo"

params = {
    "contractCode": "380630133106"
}
headers = {'Content-type': 'application/json'}
x = requests.post(get_general_info_url,
                  data=json.dumps(params),
                  headers=headers,
                  auth=HTTPBasicAuth(PORTAL_LOGIN, PORTAL_PASSWORD))
print(x.text)
