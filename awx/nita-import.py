#!/usr/bin/env python3

import requests
import sys
import json,yaml
import base64

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
    response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
    if response.status_code != 200:
      print(f"Server unavailable: {response.status_code} {response.text}")
      sys.exit()
    print ("get: "+AWX+subURL+FMT)
    return requests.get(AWX+subURL+FMT,auth=(USER,PASSWORD),headers=HEADER)

def patchAWX (subURL, dataDict):
    FMT="?format=json"
    if FMT in subURL:
       FMT=""
    HEADER={'Content-type': 'application/json', 'Accept': 'application/json'}
    response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
    if response.status_code != 200:
      print(f"Server unavailable: {response.status_code} {response.text}")
      sys.exit()
    print ("patch: "+AWX+subURL)
    return requests.patch(AWX+subURL,data=dataDict,auth=(USER,PASSWORD),headers=HEADER)
    
def postAWX (subURL, dataDict):
    FMT="?format=json"
    if FMT in subURL:
       FMT=""
    HEADER={'Content-type': 'application/json', 'Accept': 'application/json'}
    response=requests.get(AWX+"/api/login",auth=(USER,PASSWORD))
    if response.status_code != 200:
      print(f"Server unavailable: {response.status_code} {response.text}")
      sys.exit()
    print ("post: "+AWX+subURL)
    return requests.post(AWX+subURL,data=dataDict,auth=(USER,PASSWORD),headers=HEADER)
    
#
# Postman seemed to indicated the basic authentication login action is still required so stuck with basic authentication for now
# HEADER={"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Basic {encodeded_credentials}"}
#

#
# Pull existing inventory
#
inventories=getAWX("/api/v2/inventories")
dictInventory=json.loads(inventories.text)
print(dictInventory)
for count,dict in enumerate(dictInventory['results']):
    id = dict['id']
    name = dict['name']
    desc = dict['description']
    org = dict['organization']
    if name == "NITA WAN":
        print(f"ID: {id}, Org: {org} Name: {name}, Description: {desc}")
        #
        # Example on how to modify original JSON
        #
        dictInventory['results'][count]['description']="NITA Test Inventory Again"
        updated_json=json.dumps(dictInventory)
        print(updated_json)
        #
        # Update description on server
        #
        inventories=patchAWX("/api/v2/inventories/"+str(id),dataDict='{"description":"NITA Test Inventory Again"}')
        #
        # Grab the "routers" group ID
        #
        group_url = dict['related']['groups']
        groups=getAWX(group_url)
        print(groups.text)
        groupsList = json.loads(groups.text)
        print(groups.status_code)
        if groups.status_code == 200:
            for groups_dict in groupsList['results']:
                if groups_dict['name'] == "routers":
                    group_id=groups_dict['id']
                    print(f"Group ID: {group_id}")

#
#Add pe3 host to existing inventory
#
response=postAWX("/api/v2/inventories/"+str(id)+"/hosts/",pe3_data_json)
print(response.status_code)
print(response.reason)
if response.status_code==201:
    host_id=json.loads(response.text)['id']
    #
    # Patch variable data to pe3 host
    #
    #response=requests.patch(AWX+"/api/v2/hosts/"+str(host_id)+"/variable_data/",headers=HEADER,auth=(USER,PASSWORD),data=pe3_var_json)
    response=patchAWX("/api/v2/hosts/"+str(host_id)+"/variable_data/",pe3_var_json)
    print(response.status_code)
    print(response.reason)
    #
    # Add pe3 host to routers group
    #
    response=postAWX("/api/v2/hosts/"+str(host_id)+"/groups/",'{"id":'+str(group_id)+'}')
    print(response.status_code)
    print(response.reason)
else:
    print(response.text)
