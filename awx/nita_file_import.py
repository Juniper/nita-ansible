#!/usr/bin/env python3
import os
import glob
import requests
import sys
import json,yaml
import base64
from pathlib import Path

USER="awx"
PASSWORD="Juniper!1"
credentials=f"{USER}:{PASSWORD}"
encodeded_credentials=base64.b64encode(credentials.encode()).decode()
AWX="http://127.0.0.1:31768"

#from nita_import import *
#pe3_data_json=json.dumps(yaml.safe_load(pe3_data))

def get_yaml_files(project_folder):
    # Construct the path pattern for YAML files in host_vars
    yaml_files_pattern = os.path.join(project_folder, 'host_vars', '*.yaml')
    
    # Use glob to find all YAML files matching the pattern
    yaml_files = glob.glob(yaml_files_pattern)
    return yaml_files
    # Traverse and open each YAML file
    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as file:
            content = file.read()
            print(f'Contents of {yaml_file}:')
            print(content)
            print('---')

def list_directories(folder_path):
    directories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    return directories

if __name__ == "__main__":
    nita_folder = '/var/nita_project'

    
    # Example usage of list_directories
    directories = list_directories(nita_folder)
    print(f'Directories in {nita_folder}: {directories}')
    hosts={}
    for directory in directories:
        project_folder = os.path.join(nita_folder, directory)
        yaml_files=get_yaml_files(project_folder)
        for yaml_file in yaml_files:
            with open(yaml_file, 'r') as file:
                content = file.read()
                host_json=json.loads(json.dumps(yaml.safe_load(content)))
                host_name=os.path.basename(yaml_file).replace('.yaml','')
                if host_name in hosts:
                    print(f"Host {host_name} already exists")  
                else:
                    host_json["inventory"]=directory
                    hosts[host_name]=host_json 
        for index,(host,host_data) in enumerate(hosts.items()):
            host_ip = host_data["management_interface"]["ip"]
            host_inventory = host_data["inventory"]
            print(f'{host}: {host_ip} {host_inventory} {host_data}') 
            ### add host to AWX using directory name as inventory name. Not sure how else to do it without mapping X to Y
            


