import requests
import sys
import json,yaml
import base64

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