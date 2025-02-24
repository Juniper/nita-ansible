#!/usr/bin/env python3

import requests
import sys
import json,yaml
import base64

#
# Postman seemed to indicated the basic authentication login action is still required so stuck with basic authentication for now
# HEADER={"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Basic {encodeded_credentials}"}
#
USER="awx"
PASSWORD="Juniper!1"
credentials=f"{USER}:{PASSWORD}"
encodeded_credentials=base64.b64encode(credentials.encode()).decode()
AWX="http://127.0.0.1:31768"

#
# Sample Data
#
project_data="""
name: 'Sample Project'
description: 'Sample Project Description'
scm: ''
status: 'ok'
local_path: 'sample'
"""

job_template_data = """
name: 'Sample Job'
description: 'Sample Job Description'
job_type: 'run'
playbook: 'playbook.yml'
ask_inventory_on_launch: true
variables: {\"vars\": {\"temp_dir\": \"/var/tmp\", \"build_dir\": \"/var/tmp/build\", \"log\": \"/var/tmp/build/log\"} }
"""
print(job_template_data)

pe3_data="""
name: 100.123.1.3
description: Test pe3
enabled: true
"""
pe3_var="""
core_interfaces:
- desc: '*** to dc1-borderleaf1 ***'
  int: ge-0/0/0
  ip: 10.32.6.2
  mask: 30
- desc: '*** to dc1-borderleaf2 ***'
  int: ge-0/0/2
  ip: 10.32.10.2
  mask: 30
- desc: '*** to wan-pe2 ***'
  int: ge-0/0/1
  ip: 10.32.1.1
  mask: 30
healthbot_device_group: wan
loopback_ip: 10.52.100.3
management_interface:
  int: fxp0
  ip: 100.123.1.2
  mask: 16
underlay_ebgp:
- autonomous_system: 65400
  group: IPCLOS_eBGP
  neighbors:
  - asn: 65401
    name: 10.32.1.2
  - asn: 65506
    name: 10.32.6.1
  - asn: 65507
    name: 10.32.10.1
"""
pe3_data_json=json.dumps(yaml.safe_load(pe3_data))
pe3_var_json=json.dumps(yaml.safe_load(pe3_var))
project_json=json.dumps(yaml.safe_load(project_data))
job_template_json=json.dumps(yaml.safe_load(job_template_data))

def getAWX (subURL):
    FMT="?format=json"
    if FMT in subURL:
       FMT=""
    HEADER={'Content-type': 'application/json', 'Accept': 'application/json'}
    try:
      response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
      if response.status_code != 200:
        print(f"Server unavailable: {response.status_code} {response.text}")
        sys.exit()
      print ("get: "+AWX+subURL+FMT)
      return requests.get(AWX+subURL+FMT,auth=(USER,PASSWORD),headers=HEADER)
    except requests.exceptions.RequestException as e:
      print(f"Server unavailable: {e}")
      sys.exit()
    #response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
    #if response.status_code != 200:
    #  print(f"Server unavailable: {response.status_code} {response.text}")
    #  sys.exit()
    #print ("get: "+AWX+subURL+FMT)
    #return requests.get(AWX+subURL+FMT,auth=(USER,PASSWORD),headers=HEADER)

def patchAWX (subURL, jsonData):
    FMT="?format=json"
    if FMT in subURL:
       FMT=""
    HEADER={'Content-type': 'application/json', 'Accept': 'application/json'}
    try:
      response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
      #if response.status_code != 200:
      #  print(f"Server unavailable: {response.status_code} {response.text}")
      #  sys.exit()
      #print ("patch: "+AWX+subURL)
      return requests.patch(AWX+subURL,data=jsonData,auth=(USER,PASSWORD),headers=HEADER)
    except requests.exceptions.HTTPError as http_err:
      if response.status_code == 400:
        print("400 Bad Request: {http_err}")
    except requests.exceptions.RequestException as e:
      print(f"Server unavailable: {e}")
      sys.exit()
    #response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
    #if response.status_code != 200:
    #  print(f"Server unavailable: {response.status_code} {response.text}")
    #  sys.exit()
    #print ("patch: "+AWX+subURL)
    #return requests.patch(AWX+subURL,data=dataDict,auth=(USER,PASSWORD),headers=HEADER)
    
def postAWX (subURL, jsonData):
    FMT="?format=json"
    if FMT in subURL:
       FMT=""
    HEADER={'Content-type': 'application/json', 'Accept': 'application/json'}
    try:
      response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
      #if response.status_code != 200:
      #  print(f"Server unavailable: {response.status_code} {response.text}")
      #  sys.exit()
      print ("post: "+AWX+subURL)
      response=requests.post(AWX+subURL,data=jsonData,auth=(USER,PASSWORD),headers=HEADER)
      response.raise_for_status()
      
      return response
    except requests.exceptions.HTTPError as err:
      if response.status_code == 400:
        print(f"400 Bad Request: {err}")
        return "400 Bad Request"
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")



def getInventory (inventory_name):
  inventories=getAWX("/api/v2/inventories")
  dictInventory=json.loads(inventories.text)
  for dict in dictInventory['results']:
    if dict['name'] == inventory_name:
      return dict['id'],dict['description'],dict['organization'],dict  
  return 0,"","",dict   

def getJobs (orgid):
  jobs=getAWX(f"/api/v2/organizations/{orgid}/job_templates")
  job_templates=json.loads(jobs.text)
  return job_templates

def getProject (orgid):
  response=getAWX(f"/api/v2/organizations/{orgid}/projects")
  projects=json.loads(response.text)
  return projects

def getEE(environment_name,orgid):
  #Retrieves the ID of an execution environment by its name.

  try:
    response = getAWX(f"/api/v2/execution_environments/")

    if response.status_code == 200:
      # Parse the JSON response
      environments = response.json()["results"]
      for environment in environments:
        if environment["name"] == environment_name:
          return environment["id"],environment["description"],environment["image"]

    """
      #if the environment is not found in the first page, check subsequent pages
      while "next" in response.json():
        response = getAWX(response.json()["next"])
        environments = response.json()["results"]
        for environment in environments:
          if environment["name"] == environment_name:
            return environment["id"]
    """
    return None

  except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
    return None

def addHost (inventory_id, host_data, var_data):
  #Simple function to add a host to AWX inventory 
  host_id = 0
  response=postAWX(f"/api/v2/inventories/{inventory_id}/hosts/",host_data)
  if response != "400 Bad Request":
     if response.status_code == 201:
      host_id=json.loads(response.text)['id']
      response=patchAWX(f"/api/v2/hosts/{host_id}/variable_data/",pe3_var_json)
  return response, host_id

def addProject(orgid,ee_id,project):
  #Simple function to add a host to Project to AWX 
  project_id = 0
  project_dict=json.loads(project)
  project_dict['default_environment']=ee_id
  final_project=json.dumps(project_dict)
  print(final_project)
  response=postAWX(f"/api/v2/organizations/{orgid}/projects/",final_project)
  if response != "400 Bad Request":
     if response.status_code == 201:
      project_id=json.loads(response.text)['id']
  return response, project_id  

def addJobTemplate (project_id,job):
  #Simple function to add a host to add a Job Template
  job_template_id = 0
  job_dict=json.loads(job)
  job_dict["project"]=project_id
  final_job=json.dumps(job_dict)
  print(final_job)
  response=postAWX(f"/api/v2/job_templates/",final_job)
  if response != "400 Bad Request":
     if response.status_code == 201:
      job_template_id=json.loads(response.text)['id']
  return response, job_template_id 
#
# Pull existing inventory
#
orgid,desc,org,inventory=getInventory("NITA WAN")
if orgid != 0:
  print(f"ID: {orgid}, Org: {org} Name: NITA WAN, Description: {desc}")
  #
  # Example on how to modify original JSON
  #
  inventory['description']="NITA WAN"
  updated_json=json.dumps(inventory)

  #
  # Update description on server
  #
  response=patchAWX(f"/api/v2/inventories/{orgid}/",jsonData='{"description":"NITA WAN"}')

  #
  # Grab the "routers" group ID
  #
  group_url = inventory['related']['groups']
  groups=getAWX(group_url)
  print(groups.text)
  groupsList = json.loads(groups.text)
  print(groups.status_code)
  if groups.status_code == 200:
    for groups_dict in groupsList['results']:
      if groups_dict['name'] == "routers":
          group_id=groups_dict['id']
          print(f"Group ID: {group_id}")
else:
  print("Inventory not found")  
#
#  Grab NITA Project
# 
nita_project=getProject(orgid)
print(nita_project)
# 
# Grab Job Templates Inventory
#
nita_jobs=getJobs(orgid)
print(nita_jobs)

#
# Grab EE ID
#

ee_id,ee_desc,ee_image = getEE("Juniper-EE",orgid)
project_def_env = {
  "id":ee_id,
  "name":"Juniper-EE",
  "description":ee_desc,
  "image":ee_image
}


#
# Add a new project. Note the local_path must exist on the AWX task container
# It can be added manually to persistent storage area or within the container itself under /var/lib/awx/projects
#
print(project_json)
#project_dict=json.loads(project_json)
#project_dict['default_environment']=ee_id
response,project_id=addProject(orgid,ee_id,project_json)
print(response)
print(f"Project ID: {project_id}")

#(inventory_id)
# Add a job to the project
#
response,job_template_id = addJobTemplate(project_id,job_template_json)
print(job_template_id)
print(response.text)
#
#Add pe3 host to existing inventory
#
response,host_id=addHost(orgid,pe3_data_json,pe3_var_json)
# Add pe3 host to routers group
#
if host_id != 0: 
   response=postAWX(f"/api/v2/hosts/{host_id}/groups/",'{"id":'+str(group_id)+'}')
   print(response.status_code)
   print(response.reason)
