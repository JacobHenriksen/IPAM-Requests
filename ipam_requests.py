import requests
from requests.auth import HTTPBasicAuth
import sys
import os.path
from getpass import getpass
from getpass import getuser
import logging
import yaml

## LOGGING & DEBUGGING

debugging = False
if debugging is True:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)

if len(sys.argv) > 1:
    if sys.argv[1].find("--log") != -1:
        loglevel = sys.argv[1][sys.argv[1].rfind("=")+1:]

        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)

##  DISABLE WARNINGS
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

##  DEFINE VARIABLES AND URLS
URL = 'https://ipam.sca.com'
TOKEN_PATH = '/api/ipmgr/user'
USERNAME = 'jacobapi'
export_file_name = f'ipam_requests_{sys.argv[1][sys.argv[1].find('.')+2:sys.argv[1].rfind('.')]}_export.yaml'

##  RETRIEVE TOKEN
print('\nGenerating session token...')
secret=open('pwd.txt', "r")                                             #TEMPORARY, DELETE BEFORE DEPLOYMENT
post_response = requests.post(
    URL+TOKEN_PATH,
    auth=HTTPBasicAuth(USERNAME, secret.readline()),                    #TEMPORARY, DELETE BEFORE DEPLOYMENT
#    auth =HTTPBasicAuth(USERNAME, getpass()),                          #UNCOMMENT THIS LINE BEFORE DEPLOYMENT
    verify=False
)
secret.close()                                                          #TEMPORARY, DELETE BEFORE DEPLOYMENT
 
logging.debug(post_response.json())                                     #DEBUG
token = post_response.json()['data']['token']
headers = {'token': token, 'Content-Type': 'application/json'}
print('Authorization successful.')
print('Token generated.\n')


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
        with open(fileName, mode='r', encoding='utf-8-sig') as f:
            for line_num, line_content in enumerate(f):
                indexEnd=line_content.find(';') 
                ip=line_content[:indexEnd]
                if validate_ip(ip) is True and ip not in ip_list:
                    ip_list.append(ip)
                elif validate_ip(ip) is False:
                    print(f'CAUTION! Line {line_num+1}: {ip} is not a valid IP-address.')                                                
    except FileNotFoundError:
        print(f'Logfile {fileName} not found.')
        return 
    else: 
        return ip_list


def get_device(address, URL):
    response = requests.get(
        URL+'/api/ipmgr/devices/search/'+address,
        headers = {'token': headers['token']},
        verify=False,
    )
    logging.debug(response.json())
    return response.json()

def print_output(device, address):
    if device['success'] is True:
        print(f'IP: {device['data'][0]['ip']} | Hostname: {device['data'][0]['hostname']} | Description: {device['data'][0]['description']}')
    else:
        print(f'Device IP {address} not found.')

def export(ip_list, export_file_name):

    response = {}
    for address in ip_list:
        device = get_device(address, URL)
        if device['success'] is True:
            response[address]=device['data'][0]['hostname'].strip()+' | '+device['data'][0]['description'].strip()
            response[address]
        else:
            response[address]='Device not found.'

    print(f'Exporting to {export_file_name}\n')
    with open(export_file_name, 'a') as file:
        yaml.dump(response, file)

def availArgs():
	print('Valid arguments:')
	print('\tprint\t- Print output.')
	print('\texport\t- Export output in .yaml-format.\n')

def main():
    if len(sys.argv) == 1:
        print('Please provide a valid .csv-file.')
    else:
        fileName = sys.argv[1]
        if len(sys.argv) == 2:
            print('Missing argument.')
            availArgs()
        elif len(sys.argv) == 3:
            option = sys.argv[2].lower()
            ip_list = read_csv(sys.argv[1])
            if option == 'print':
                print(f'\nRequesting device information from {URL}...')
                for address in ip_list:
                    device = get_device(address, URL)
                    print_output(device, address)
            elif option == 'export':
                print(f'\nRequesting device information from {URL}...')
                export(ip_list, export_file_name)
            else:
                print('\nInvalid argument.\n')
                availArgs()
        else:
            print('\nInvalid input.')

if __name__ == "__main__":
    main()
