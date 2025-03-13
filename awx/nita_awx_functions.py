import requests
import sys
import json,yaml
import base64

USER="awx"
PASSWORD="Juniper!1"
credentials=f"{USER}:{PASSWORD}"
encodeded_credentials=base64.b64encode(credentials.encode()).decode()
AWX="http://127.0.0.1:31768"

def getAWX (subURL,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
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

def patchAWX (subURL, jsonData,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
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
    
def postAWX (subURL, jsonData,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
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


def getInventory (inventory_name,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  inventories=getAWX("/api/v2/inventories",AWX,USER,PASSWORD)
  dictInventory=json.loads(inventories.text)
  for dict in dictInventory['results']:
    if dict['name'] == inventory_name:
      return dict,dict['id'],dict['description'],dict['organization']  
  return dict,0,"",0   

def getJobs (orgid,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  jobs=getAWX(f"/api/v2/organizations/{orgid}/job_templates",AWX,USER,PASSWORD)
  job_templates=json.loads(jobs.text)
  return job_templates

def getOrg (inventory_name,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  org=getAWX("/api/v2/organizations",AWX,USER,PASSWORD)
  dictOrg=json.loads(org.text)
  for dict in dictOrg['results']:
    if dict['name'] == inventory_name:
      return dict,dict['id']  
  return dict,0

def getProject (orgid,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  response=getAWX(f"/api/v2/organizations/{orgid}/projects",AWX,USER,PASSWORD)
  projects=json.loads(response.text)
  return projects

def getEE(environment_name,orgid,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  #Retrieves the ID of an execution environment by its name.

  try:
    response = getAWX(f"/api/v2/execution_environments/",AWX,USER,PASSWORD)

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

def addHost (inventory_id, host_data, var_data,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  #Simple function to add a host to AWX inventory 
  host_id = 0
  response=postAWX(f"/api/v2/inventories/{inventory_id}/hosts/",host_data,AWX,USER,PASSWORD)
  if response != "400 Bad Request":
     if response.status_code == 201:
      host_id=json.loads(response.text)['id']
      response=patchAWX(f"/api/v2/hosts/{host_id}/variable_data/",var_data,AWX,USER,PASSWORD)
  return response, host_id

def addInventory(orgid,invname,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  #Simple function to add Inventory to Project to AWX 
  inventory_id = 0
  inventory_dict={}
  inventory_dict['name']=invname
  inventory_dict['description']=invname
  inventory_dict['organization']=orgid
  final_inventory=json.dumps(inventory_dict)
  print(inventory_dict)
  response=postAWX(f"/api/v2/inventories/",final_inventory,AWX,USER,PASSWORD)
  if response != "400 Bad Request":
     if response.status_code == 201:
      inventory_id=json.loads(response.text)['id']
  return response, inventory_id  

def addOrg(orgname,description,ee_id,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  #Simple function to add Organization to AWX 
  org_id = 0
  org_dict={}
  org_dict['name']=orgname
  org_dict['description']=description
  org_dict['default_environment']=ee_id
  final_org=json.dumps(org_dict)
  print(final_org)
  response=postAWX("/api/v2/organizations/",final_org,AWX,USER,PASSWORD)
  if response != "400 Bad Request":
     if response.status_code == 201:
      org_id=json.loads(response.text)['id']
  return response, org_id

def addProject(orgid,ee_id,project,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  #Simple function to add a host to Project to AWX 
  project_id = 0
  project_dict=json.loads(project)
  project_dict['default_environment']=ee_id
  final_project=json.dumps(project_dict)
  print(final_project)
  response=postAWX(f"/api/v2/organizations/{orgid}/projects/",final_project,AWX,USER,PASSWORD)
  if response != "400 Bad Request":
     if response.status_code == 201:
      project_id=json.loads(response.text)['id']
  return response, project_id  

def addJobTemplate (project_id,job,AWX=AWX,USER=USER,PASSWORD=PASSWORD):
  #Simple function to add a host to add a Job Template
  job_template_id = 0
  job_dict=json.loads(job)
  job_dict["project"]=project_id
  final_job=json.dumps(job_dict)
  print(final_job)
  response=postAWX(f"/api/v2/job_templates/",final_job,AWX,USER,PASSWORD)
  if response != "400 Bad Request":
     if response.status_code == 201:
      job_template_id=json.loads(response.text)['id']
  return response, job_template_id 