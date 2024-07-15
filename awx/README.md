# nita-awx

This is being used to test the AWX execution environment. AWX requires kubernetes.

## Folders

<b>ansible-ee</b> - setup files to build ansible execution environment based on https://github.com/juniper/nita-ansible container.


## Installation

1. Install Kubernetes. The build script assumes kubernetes is already installed. 

2. Install AWX using the provided script as show below. This does a few things in addition to pulling a specific version of AWX. The script creates a namespace in k8s called ```awx```. It also creates the pods required to run AWX and spins up a service running on default ports for AWX. 

```
cd nita-ansible
./build_awx_container.sh
```

3. After install AWX, you will need to retrieve the admin password to login into the AWX console.

```
kubectl -n awx get secret  awx-admin-password -o jsonpath="{.data.password}" | base64 --decode
```

4. Login into the webconsole at localhost:31768 and change the user password (if desired) with username admin and the password decoded above. 

<img width="1502" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/fca0a3b0-d75e-480d-8fd1-38d982799fcd">

5. Setup execution environment for NITA.

See [ansible-ee/README.md](/ansible-ee/README.md)  for details.

## Coming Soon

NITA has been ported to k8s so we can being integration work with AWX.  


## AWX Screenshots

How the NITA example data is being loaded into AWX for testing.

### Template
<img width="1526" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/5820f15e-a9ff-44c9-b48b-d209b5ca6923">


### Project

<img width="1505" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/de5572ab-6707-415a-94e0-f9d8765dee99">

### Template

<img width="1950" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/262a6242-8128-491d-86e2-70d82391b49e">


### Inventories

Note the variable data from ``groups_vars``. Also AWX requires an additional variable definition here ``ansible_python_interpreter: "{{ ansible_playbook_python }}"`` otherwise it will toss a missing module error because it runs the wrong python environment. See [this](https://www.reddit.com/r/ansible/comments/rb80pv/execution_environments_and_pip_module_locations/) thread. 

<img width="1269" alt="image" src="https://github.com/wildsubnet/nita-awx/assets/6110061/958f3a4e-c262-4c8d-b92a-b1d56ea40204">

Hosts also need to be put in a logically equivalent group based on the ansible playbook. So for the NITA example, create a group called ``routers``

<img width="1963" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/405ba267-aa2d-42e7-9900-cb0824bfb963">

### Hosts

Under hosts create individual hosts (note the variable information per host).  Currently demo doesn't have name resolution working so the name field has specific IPs. If name resolution is setup the resolvable name can be used or add the ansible_host variable (shown below).

<img width="1889" alt="image" src="https://github.com/user-attachments/assets/b258ac34-6f7a-4a13-b57f-f96ded67dd26">

Details page. Under the groups tab you will add the host to the relevant playbook group.

<img width="1894" alt="image" src="https://github.com/user-attachments/assets/604b8fe7-ffa9-476c-8e0a-0d12f38d2dad">




