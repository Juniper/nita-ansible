#!/usr/bin/env python3
import os
import glob
import requests
import sys
import json,yaml
import base64

from "nita-import" import *
pe3_data_json=json.dumps(yaml.safe_load(pe3_data))

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
    for directory in directories:
        project_folder = os.path.join(nita_folder, directory)
        yaml_files=get_yaml_files(project_folder)
        print(yaml_files)
        #for yaml_file in yaml_files:
        #    with open(yaml_file, 'r') as file:
        #        content = file.read()
        #        print(f'Contents of {yaml_file}:')
        #        print(content)
        #        print('---')

