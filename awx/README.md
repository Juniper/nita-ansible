# nita-awx

This is being used to test the AWX execution environment. AWX requires kubernetes.

## Folders and Files

<b>ansible-ee</b> - setup files to build ansible execution environment based on https://github.com/juniper/nita-ansible container.

<b>nita_awx_functions.py</b> - Front end function calls to add/update elements inside of AWX. Used by nita_file_import.py.

<b>nita_file_import.py</b> - Recursively traverses folders in a folder called ``nita_project`` in the AWX host OS working directory (assumes /data/projects) and creates NITA project and uploads host information to AWX.

Other files are used to install AWX.

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

## To-Do

1. Continue debugging effort for NITA Project Import
2. Integrate with NITA Webapp
3. Debug template/playbooks (some playbooks that call shell scripts seem to be problematic)  


## AWX Screenshots

How the NITA example data is being loaded into AWX for testing.

### Organization
<img width="1896" alt="image" src="https://github.com/user-attachments/assets/afc18676-edf0-4df0-9825-40e65adff6c1" />

### Execution Environment
<img width="1883" alt="image" src="https://github.com/user-attachments/assets/80b1a0c2-73c9-4d49-9a0e-9fc0917e81e4" />

### Project
<img width="1893" alt="image" src="https://github.com/user-attachments/assets/89d1eab7-5a5f-47cf-92d5-2156b1939c4d" />

### Template
<img width="1892" alt="image" src="https://github.com/user-attachments/assets/7e3d7221-df7c-428e-9268-cd2436d21ba4" />

### Inventories
<img width="1875" alt="image" src="https://github.com/user-attachments/assets/e31e9741-4793-438a-b642-a158754cbb92" />

Inventories are named based on the project folder name under the ``nita_project`` folder.

<img width="1889" alt="image" src="https://github.com/user-attachments/assets/7ac57d34-b3a1-4d7b-82cb-1dfd65d3f21e" />

Note the variable data under the inventory. This is imported from ``all.yaml`` in ``group_vars`` folder in the project folder. AWX doesn't allow the creation of an explicity all group as it is already implicitly defined so the related variable data is stored at the inventory level. 

In certain cases AWX may require an additional variable definition here ``ansible_python_interpreter: "{{ ansible_playbook_python }}"`` otherwise it will toss a missing module error because it runs the wrong python environment. See [this](https://www.reddit.com/r/ansible/comments/rb80pv/execution_environments_and_pip_module_locations/) thread. 

Groups are created and populated with host information if defined in the project folder ``hosts`` file.

<img width="1888" alt="image" src="https://github.com/user-attachments/assets/af5f160a-65b9-44f2-a0cf-b501ce1549f5" />

<img width="1594" alt="image" src="https://github.com/user-attachments/assets/5b55d8cb-73c1-4d0a-a059-d51b2314a523" />

### Hosts
<img width="1876" alt="image" src="https://github.com/user-attachments/assets/926a78bc-ffd9-4feb-a750-df4412dc03b5" />

<img width="1881" alt="image" src="https://github.com/user-attachments/assets/352e4a04-45be-474c-b26c-57fd616839cd" />

### Templates
<img width="1887" alt="image" src="https://github.com/user-attachments/assets/d162b05b-fe19-4d45-8df0-dadad328c0a7" />

### Executed Job
<img width="1876" alt="image" src="https://github.com/user-attachments/assets/d132c19e-544e-4577-ab40-40fe7a52bf79" />





