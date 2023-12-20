import requests
from requests.auth import HTTPBasicAuth
from getpass import getpass

##  DISABLE WARNINGS
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

##  DEFINE URLS AND USER CREDENTIALS
URL = 'https://ipam.sca.com/'
USERNAME = ''
PASSWORD = ''





if __name__ == "__main__":

password = getpass()