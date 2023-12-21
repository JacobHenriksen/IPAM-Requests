import requests
from requests.auth import HTTPBasicAuth
import sys
import os.path
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
    auth =HTTPBasicAuth(USERNAME, 'qHq4cRIypR41hqZkdPY1'),                  #THIS LINE SHOULD BE COMMENTED BEFORE COMMIT
#    auth =HTTPBasicAuth(USERNAME, getpass()),                              #UNCOMMENT THIS LINE BEFORE GIT COMMIT
    verify=False
)

#print(post_response.json())                                                #DEBUG
token = post_response.json()['data']['token']
headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
print('Token recieved.')
#print(f'Token: {token}')                                                   #DEBUG

def validate_ip(ip):
    a = ip.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def read_csv(fileName):
    ip_list=[]
    try:
        with open(fileName, mode='r') as f:
            for line in f:
                indexEnd=line.find(';')-1 
                ip=line[:indexEnd]
                if validate_ip(ip) == True and ip not in ip_list:
                    ip_list.append(ip)
#        print(ip_list)                                                 
    except FileNotFoundError:
        print(f'Logfile {fileName} not found.')
        return 
    else: 
        return ip_list



def availArgs():
	pass

if __name__ == "__main__":
    read_csv('test.csv')

""" 	if len(sys.argv) == 1:
		print('Please provide a valid .csv-file.')
	else:
		fileName = sys.argv[1]
		if len(sys.argv) == 2:
			print('Missing argument.')
			availArgs()
		elif len(sys.argv) == 3:
			argument = sys.argv[2]
			if argument == 'count':
				count(fileName)
			elif argument == 'list':
				makeList(fileName)
			else:
				print('\nInvalid argument.\n')
				availArgs()
		else:
			print('\nInvalid input.') """
