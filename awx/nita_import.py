#!/usr/bin/env python3
from nita_awx_functions import *
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

from nita_awx_functions import *
#
# Pull existing inventory
invid,desc,orgid,inventory=getInventory("NITA")
if orgid != 0:
  print(f"ID: {invid}, Org: {orgid} Name: NITA, Description: {desc}")
  #
  # Example on how to modify original JSON
  #
  inventory['description']="NITA Hosts"
  updated_json=json.dumps(inventory)

  #
  # Update description on server
  #
  response=patchAWX(f"/api/v2/inventories/{orgid}/",jsonData='{"description":"NITA Hosts"}')

  #
  # Grab the "routers" group ID
  #
  group_url = inventory['related']['groups']
  groups=getAWX(group_url)
  print(groups.text)
  groupsList = json.loads(groups.text)
  print(groups.status_code)
  group_id=0
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

#
# Add a new job_template. Note the local_path must exist on the AWX task container with playbook file
# It can be added manually to persistent storage area or within the container itself under /var/lib/awx/projects
# 
response,job_template_id = addJobTemplate(project_id,job_template_json)
print(job_template_id)
#print(response.text)
#
#Add pe3 host to existing inventory
#
response,host_id=addHost(invid,pe3_data_json,pe3_var_json)
# Add pe3 host to routers group
#
if host_id != 0: 
   response=postAWX(f"/api/v2/hosts/{host_id}/groups/",'{"id":'+str(group_id)+'}')
   print(response.status_code)
   print(response.reason)
