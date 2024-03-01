import requests
from requests.auth import HTTPBasicAuth
import sys
import os.path
from getpass import getpass, getuser                                # Might not be needed 
import logging
import yaml
import csv

## LOGGING & DEBUGGING

debugging = False
#debugging = True
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
#URL = 'https://ipamtest.sca.com'                                            #TEST URL
APP_ID = 'python'
TOKEN_PATH = f'/api/{APP_ID}/user'
USERNAME = 'jacobapi'
export_file_name = f'{sys.argv[1][sys.argv[1].find('.')+2:sys.argv[1].rfind('.')]}_ipam_search_export.yaml'


# GENERATING SESSION TOKEN
def request_token():
    secret=open('pwd.txt', "r")                                             #TEMPORARY, DELETE BEFORE DEPLOYMENT
    post_response = requests.post(
        URL+TOKEN_PATH,
        auth=HTTPBasicAuth(USERNAME, secret.readline()),                    #TEMPORARY, DELETE BEFORE DEPLOYMENT
    #    auth =HTTPBasicAuth(USERNAME, getpass()),                          #UNCOMMENT THIS LINE BEFORE DEPLOYMENT
        verify=True
    )
    secret.close()  

    if post_response.json()['success'] is not True:
        print(f'Error: {post_response.json()['code']} {post_response.json()['message']}')
        return False
    else:                                                     
        logging.debug(post_response.json())                                     #DEBUG
        token = post_response.json()['data']['token']
        return token


# VALIDATING IPV4 FORMAT
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


# READING PROVIDED CSV-FILE AND APPENDING TO LIST
def read_csv(fileName):
    print(f'Reading {fileName}... ')
    ip_list=[]
    try:
        with open(fileName, mode='r', encoding='utf-8-sig') as f:
            for line_num, line_content in enumerate(f):
                indexEnd=line_content.find(';') 
                ip=line_content[:indexEnd]
                if validate_ip(ip) is True and ip not in ip_list:
                    ip_list.append(ip)
                elif validate_ip(ip) is False:
                    if validate_ip(ip) != '':
                        print(f'CAUTION! line {line_num+1}, invalid IP-address: {ip}')                                                
    except FileNotFoundError:
        print(f'Logfile {fileName} not found.')
        return 
    else: 
        return ip_list


# MAKING GET REQUEST FOR IP-ADDRESSES
def get_device(device_address, URL, token):
    headers = {'token': token, 'Content-Type': 'application/json'}
    response = requests.get(
        f'{URL}/api/{APP_ID}/search/{device_address}/',
        headers = {'token': headers['token']},
        params = {'addresses': 1, 
                  'subnets': 0,
                  'vlan': 0,
                  'vrf': 0},
        verify=True,
        )
    logging.debug(response.json())
    return response.json()




# PRINTING THE RESULT
def print_output(device, device_address):
    device_data = device['data']['addresses']['data'][0]
    if device['success'] is True and device['data']['addresses']['data'] != 'No addresses found':
        if device_data['description'] is None:
            print(f"IP: {device_address:<20} | Hostname: {device_data['hostname']:<40} | Description: ")
        else:
            print(f"IP: {device_address:<20} | Hostname: {device_data['hostname']:<40} | Description: {device_data['description']}")

    else:
        print(f'Device IP {device_address} not found.')


# EXPORTING THE RESULT AS YAML
def export_yaml(ip_list, export_file_name, token):
    print(f'\nRequesting device information from {URL}...')
    export_data = []
    for device_address in ip_list:
        device = get_device(device_address, URL, token)
        device_data = device['data']['addresses']['data'][0]
        if device['success'] is True and device['data']['addresses']['data'] != 'No addresses found':
            if device_data['description'] is None:
                export_data.append({'IP': device_address, 'Hostname': device_data['hostname'], 'Description': None})
            else:
                export_data.append({'IP': device_address, 'Hostname': device_data['hostname'], 'Description': device_data['description']})
        else:
            export_data.append({'IP': device_address, 'Hostname': 'Device not found.', 'Description': None})

    print(f'Exporting to {export_file_name}\n')
    with open(export_file_name, 'a') as yamlfile:
        yaml.dump(export_data, yamlfile, default_flow_style=False, sort_keys=False)


# EXPORTING THE RESULT AS CSV                           BROKEN
def export_csv(ip_list, export_file_name, token):
    print(f'\nRequesting device information from {URL}...')
    export_data = []
    for device_address in ip_list:
        device = get_device(device_address, URL, token)
        device_data = device['data']['addresses']['data'][0]
        if device['success'] is True and device['data']['addresses']['data'] != 'No addresses found':
            if device_data['description'] is None:
                export_data.append({'IP': device_address, 'Hostname': device_data['hostname'], 'Description': None})
            else:
                export_data.append({'IP': device_address, 'Hostname': device_data['hostname'], 'Description': device_data['description']})
        else:
            export_data.append({'IP': device_address, 'Hostname': 'Device not found.', 'Description': None})

    print(f'Exporting to {export_file_name}\n')
    with open(export_file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        writer.writerow(['IP', 'Hostname', 'Description'])
        
        # Write data rows
        for item in export_data:
            writer.writerow([item['IP'], item['Hostname'], item['Description']])


# PRINTING AVAILABLE CLI ARGUMENTS
def availArgs():
    print('Valid arguments:')
    print('\tprint\t- Print output.')
    print('\texport\t- Export output in .yaml-format.\n')
    print('\tcount\t - Count number of devices.\n')

# MAIN
def main():
    print()
    if len(sys.argv) == 1:
        print('Please provide a valid .csv-file.')
    else:
        fileName = sys.argv[1]
        if len(sys.argv) == 2:
            print('Missing argument.')
            availArgs()
        elif len(sys.argv) == 3:
            token = request_token()
            if token is False:
                return
            else:
                option = sys.argv[2].lower()
                ip_list = read_csv(sys.argv[1])
                if option == 'print':
                    print(f'\nRequesting device information from {URL}...')
                    for device_address in ip_list:
                        device = get_device(device_address, URL, token)
                        print_output(device, device_address)
                    print()
                elif option == 'export':
                    export_yaml(ip_list, export_file_name, token)
                elif option == 'count':
                    print(len(ip_list))
                else:
                    print('\nInvalid argument.\n')
                    availArgs()
        else:
            print('\nInvalid input.')


if __name__ == "__main__":
    main()
    print()
