import requests
from requests.auth import HTTPBasicAuth
from getpass import getpass
from getpass import getuser

##  DISABLE WARNINGS
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

##  DEFINE URLS
URL = 'https://ipam.sca.com'
TOKEN_PATH = '/api/ipmgr/user'
USERNAME = 'jacobapi'

##  RETRIEVE TOKEN
print('\nRetrieving token...\n')
post_response = requests.post(
    URL+TOKEN_PATH,
    auth =HTTPBasicAuth(USERNAME, getpass()),
    verify=False
)

#print(post_response.json())                                                #DEBUG
token = post_response.json()['data']['token']
headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
print('Token recieved.')
#print(f'Token: {token}')                                                   #DEBUG


if __name__ == "__main__":
    pass

