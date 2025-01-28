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

def patchAWX (subURL, dataDict):
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
      return requests.patch(AWX+subURL,data=dataDict,auth=(USER,PASSWORD),headers=HEADER)
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
    
def postAWX (subURL, dataDict):
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
      response=requests.post(AWX+subURL,data=dataDict,auth=(USER,PASSWORD),headers=HEADER)
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

def addHost (inventory_id, host_data, var_data):
  #Simple function to add a host to AWX inventory 
  host_id = 0
  response=postAWX("/api/v2/inventories/"+str(inventory_id)+"/hosts/",host_data)
  if response != "400 Bad Request":
     if response.status_code == 201:
      host_id=json.loads(response.text)['id']
      response=patchAWX("/api/v2/hosts/"+str(host_id)+"/variable_data/",pe3_var_json)
  return response, host_id

def getInventory (inventory_name):
  inventories=getAWX("/api/v2/inventories")
  dictInventory=json.loads(inventories.text)
  for dict in dictInventory['results']:
    if dict['name'] == inventory_name:
      return dict['id'],dict['description'],dict['organization'],dict  
  return 0,"","",dict   


#
# Pull existing inventory
#
id,desc,org,inventory=getInventory("NITA WAN")
if id != 0:
  print(f"ID: {id}, Org: {org} Name: NITA WAN, Description: {desc}")
  #
  # Example on how to modify original JSON
  #
  inventory['description']="NITA WAN"
  updated_json=json.dumps(inventory)

  #
  # Update description on server
  #
  response=patchAWX("/api/v2/inventories/"+str(id),dataDict='{"description":"NITA WAN"}')

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
#Add pe3 host to existing inventory
#
response,host_id=addHost(id,pe3_data_json,pe3_var_json)
# Add pe3 host to routers group
#
if host_id != 0: 
   response=postAWX("/api/v2/hosts/"+str(host_id)+"/groups/",'{"id":'+str(group_id)+'}')
   print(response.status_code)
   print(response.reason)
