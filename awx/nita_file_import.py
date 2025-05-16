#!/usr/bin/env python3
import os
import glob
import yaml

from pathlib import Path




from nita_awx_functions import *

#from nita_import import *
#pe3_data_json=json.dumps(yaml.safe_load(pe3_data))

def get_yaml_files(project_folder,subfolder):
    # Construct the path pattern for YAML files in host_vars
    yaml_files_pattern = os.path.join(project_folder, subfolder, '*.yaml')
    
    # Use glob to find all YAML files matching the pattern
    yaml_files = glob.glob(yaml_files_pattern)
    return yaml_files
    # Traverse and open each YAML file


def get_ansible_hosts(project_folder):
    host_file = os.path.join(project_folder, 'hosts')
    with open(host_file, 'r') as file:
        content = file.read()
    # Parse the content of the file
    groups = {}
    current_group = None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            current_group = line[1:-1]
            groups[current_group] = []
        elif current_group:
            groups[current_group].append(line)
    return groups
     

def list_directories(folder_path):
    directories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    return directories

if __name__ == "__main__":
    user="awx"
    password="Juniper!1"
    credentials=f"{user}:{password}"
    encodeded_credentials=base64.b64encode(credentials.encode()).decode()
    awx="http://127.0.0.1:31768"
    #
    # NITA files need to be copied to AWX persistent volume
    # cp -r /var/nita_project /data/projects/
    # This allows playbooks to be run from the AWX GUI
    #
    proj_folder = '/data/projects/nita_project'
    playbook_directory = 'nita_project'
    #
    # Create Execution Environment
    #
    response,ee_id=add_ee("Juniper-EE","Juniper awx EE","localhost:5000/nita-ansible-ee","always",awx,user,password)
    print(f"{ee_id} {response}")
    #
    # Add Org and Project
    response,org_id=add_org("NITA","NITA Organization",ee_id,awx,user,password)

    response, project_id=add_project("NITA Project","NITA Project",org_id,ee_id,playbook_directory,awx,user,password)
    print(f"{project_id} {response}")

    directories = list_directories(proj_folder)
    print(f'Directories in {proj_folder}: {directories}')
    hosts={}
    inventory={}
    for directory in directories:
        #
        # Add directory as new inventory to use in add host
        #
        response,inv_id = add_inventory(org_id,directory,awx,user,password)
        if inv_id != 0:
            inventory[directory]=inv_id
        project_folder = os.path.join(proj_folder, directory)
        ansible_groups=get_ansible_hosts(project_folder)
        #
        # Parse Host Data
        #
        host_files=get_yaml_files(project_folder,'host_vars')
        for yaml_file in host_files:
            with open(yaml_file, 'r') as file:
                content = file.read()
                host_json=json.loads(json.dumps(yaml.safe_load(content)))
                host_name=os.path.basename(yaml_file).replace('.yaml','')
                if host_name in hosts:
                    print(f"Host {host_name} already exists")  
                else:
                    host_json["inventory"]=directory
                    host_json["ansible_host"]=host_json["management_interface"]["ip"]
                    hosts[host_name]=host_json 
        with open ('hosts.txt', 'w',encoding='utf-8') as hostfile:
            for index,(host,host_data) in enumerate(hosts.items()):
                host_ip = host_data["management_interface"]["ip"]
                host_inventory = inventory[host_data["inventory"]]
                host_dict=dict(name=host,description=host_ip,enabled=True)
                host_id=0
                print(f'{host_dict} {host_data}') 
                
                response,host_id=add_host(host_inventory,json.dumps(host_dict),json.dumps(host_data),awx,user,password)
                if response!="400 Bad Request":
                    print(f"Host added ID: {host_id}")
                    hostfile.write(f'{host_ip} {host}\n')
                elif host_id!=0:
                    print(f"Host exists ID: {host_id} ")
                    hostfile.write(f'{host_ip} {host}\n')
                else:
                    print(f"Error adding host: {response}")
                print('---------------------------')
        #
        # Grab build project file (should only be one)
        # This may require a change cli commands to create folder structure in AWX (researching)
        # 
        hostfile.close()
        build_file=get_yaml_files(project_folder,'build')
        print(f"Build file: {build_file} {directory}")
        job_name=f"name: {directory}-build"
        playbook_file=f"playbook: {directory}/build/{os.path.basename(build_file[0])}"
        job_template_data = """
job_type: 'run'
ask_inventory_on_launch: false
ask_credential_on_launch: false
ask_verbosity_on_launch: false
"""
        extra_vars='{"vars": {"temp_dir": "/var/tmp", "build_dir": "/var/tmp/build", "log": "/var/tmp/build/log"}}'

        job_template_data = job_name+'\n'+playbook_file+job_template_data
        response,job_template_id=add_job_template(project_id,inv_id,ee_id,json.dumps(yaml.safe_load(job_template_data)),json.dumps(yaml.safe_load(extra_vars)),awx,user,password)
        print(f"Job Template ID: {job_template_id}")
        #
        # Parse group data
        # Need to update group data with variable information
        #
        for group, grhosts in ansible_groups.items():
            #group_dict=dict(name=group,description=group)
            if group.count(':') == 1:
                # add group to inventory
                #
                response, group_id = add_inv_group(group,group,inv_id,awx,user,password)
                if response!="400 Bad Request":
                    print(f"Parent group added ID: {group_id}")
                else:
                    print(f"Parent group exists ID: {group_id} ")
                for child in grhosts:
                    print(f"Child group: {child}")  
                    response, child_id = add_inv_group(child,child,inv_id,awx,user,password)
                    if response!="400 Bad Request":
                        print(f"Child group added ID: {child_id}")
                    else:
                        print(f"Child group exists ID: {child_id} ")
                    if child_id != 0:
                        response = add_child_to_group(child_id,group_id,awx,user,password)
                        if response!="400 Bad Request":
                            print(f"Child group added to parent group ID: {child_id}")
                        else:
                            print(f"Child group exists in parent group ID: {child_id} ")
            else:
                # add additional groups to inventory or grab group_id if already exists from parent group creation
                # above
                response, group_id = add_inv_group(group,group,inv_id,awx,user,password)
                if response!="400 Bad Request":
                    print(f"Group added ID: {group_id}")
                else:
                    print(f"Group exists ID: {group_id} ")
            
                # Add hosts to group
                #
                for grhost in grhosts:
                    print(f"Host: {grhost}")
                    response, host_id = get_host(grhost,inv_id,awx,user,password)
                    print(f"{grhost} host_id: {host_id} group_id: {group_id}")
                    if host_id != 0:                        
                        response = add_host_to_group(host_id,group_id,awx,user,password)
                        if response!="400 Bad Request":
                            print(f"Host added to group ID: {host_id}")
                        else:
                            print(f"Host exists in group ID: {host_id} ")


            


