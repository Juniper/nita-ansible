<H1> AWX Execution Environment </H1>

Files located in this directory are used to create ansible execution environment for AWX/Ansible Tower. the ```build-container.sh``` script calls ansible-builder, which needs to be installed using pip (see https://ansible-builder.readthedocs.io/en/stable/installation/). Ansible-builder requires python3.8 or later to execute. [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) and [Docker](https://docs.docker.com/engine/install/ubuntu/) also need to be installed.  You can also build the container directly by issuing the following commands:

```
cd context
docker build  --tag "juniper/nita-ansible-ee:22.9" .
```

AWX requires ansible EEs to be pulled from a repository. For testing purposes you can setup a local repository. See the instructions at https://www.docker.com/blog/how-to-use-your-own-registry-2/. After building the container, you can add a local repository as follows:

```
docker run -d -p 5000:5000 --restart always --name registry registry
docker tag <Ansible-ee-container-image-id> "localhost:5000/ansible-ee"
docker push localhost:5000/ansible-ee
```

After this simply define the localhost:5000/ansible-ee in your definition for an Execution Environment in AWX:

![image](https://user-images.githubusercontent.com/6110061/187557638-8b0e00bf-9cfc-4f53-9ef3-c97e7fdf0ad0.png)

<H2> Notes </H2>

+ The file ``bindep.txt`` and related configuration in ``nita-ansible-ee.yml`` are here for completeness. AWX documentation and some blogs indicated it is required although container seemed to build and operate fine without it.
+ This container is being tested against a version of the ebgp-wan example from the NITA project. Current files for the AWX test version can be found at  https://github.com/wildsubnet/awx-test. There are certain incompatiabilities between NITA environment and AWX need to be worked out (see todo list below)

## To-Do

See https://github.com/users/wildsubnet/projects/1 for current list. Issues can be found at https://github.com/wildsubnet/nita-awx/issues


## AWX Screenshots

How the NITA example data is being loaded into AWX for testing (as of September 22, 2022).

### Template
<img width="1255" alt="image" src="https://user-images.githubusercontent.com/6110061/236244860-1bf9d65b-f034-4d35-88c4-b904def590c1.png">


### Project

![image](https://user-images.githubusercontent.com/6110061/191846831-1f8644e1-96e2-496d-b77e-5a127d46ea61.png)

### Inventories

Note the variable data from ``groups_vars``. Also AWX requires an additional variable definition here ``ansible_python_interpreter: "{{ ansible_playbook_python }}"`` otherwise it will toss a missing module error because it runs the wrong python environment. See [this](https://www.reddit.com/r/ansible/comments/rb80pv/execution_environments_and_pip_module_locations/) thread.

<img width="1269" alt="image" src="https://github.com/wildsubnet/nita-awx/assets/6110061/958f3a4e-c262-4c8d-b92a-b1d56ea40204">

### Hosts

Each individual host has ``host_vars`` defined here 

<img width="1277" alt="image" src="https://user-images.githubusercontent.com/6110061/235500135-b8bf91ca-a3f5-49a4-a625-a5820bba60e4.png">
<img width="1277" alt="image" src="https://user-images.githubusercontent.com/6110061/191847262-1cefe0fa-5960-4513-8c06-a37247fa4aa3.png">

### Instance Groups

In order to mount /var/tmp into ansible execution environment, you need to update the yaml file for the container group that creates the AWX worker.  
<img width="1274" alt="image" src="https://user-images.githubusercontent.com/6110061/235755603-e99723e2-d46a-4533-bd7e-c392d94c8f17.png">

Example file:
```
apiVersion: v1
kind: Pod
metadata:
  namespace: awx
spec:
  serviceAccountName: default
  automountServiceAccountToken: false
  containers:
    - image: quay.io/ansible/awx-ee:latest
      name: worker
      args:
        - ansible-runner
        - worker
        - '--private-data-dir=/runner'
      volumeMounts:
        - mountPath: /var/tmp
          name: nb-volume
          readOnly: false
  volumes:
    - hostPath:
        path: /var/tmp
        type: ""
      name: nb-volume
```

