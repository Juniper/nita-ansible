#!/usr/bin/env python3
import os
import glob
import yaml

from pathlib import Path




from nita_awx_functions import *

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
    user="awx"
    password="Juniper!1"
    credentials=f"{user}:{password}"
    encodeded_credentials=base64.b64encode(credentials.encode()).decode()
    awx="http://127.0.0.1:31768"
    nita_folder = '/var/nita_project'
    #
    # Create Execution Environment
    #
    response,eeid=add_ee("Juniper-EE","Juniper awx EE","localhost:5000/nita-ansible-ee","always",awx,user,password)
    print(f"{eeid} {response}")
    response,orgid=add_org("NITA","NITA Organization",eeid,awx,user,password)

    directories = list_directories(nita_folder)
    print(f'Directories in {nita_folder}: {directories}')
    hosts={}
    inventory={}
    for directory in directories:
        #
        # Add directory as new inventory to use in add host
        #
        response,invid = add_inventory(orgid,directory,awx,user,password)
        if invid != 0:
            inventory[directory]=invid
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
            host_inventory = inventory[host_data["inventory"]]
            host_dict=dict(name=host_ip,description=host,enabled=True)
            print(f'{host_dict} {host_data}') 
            print('---------------------------')
            response,host_id=add_host(host_inventory,json.dumps(host_dict),json.dumps(host_data),awx,user,password)

            


