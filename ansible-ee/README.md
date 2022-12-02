<H1> AWX Execution Environment </H1>

Files located in this directory are used to create ansible execution environment for AWX/Ansible Tower. the ```build-container.sh``` script calls ansible-builder, which needs to be installed using pip (see https://ansible-builder.readthedocs.io/en/stable/installation/). Ansible-builder requires python3.8 or later to execute. You can also build the container directly by issuing the following commands:

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

* Persistence for generated configuration files. Playbooks are running and configurations seem to be getting generated but they are lost as soon as the environment is stopped. Will need a mechanism to save configuration files.
* Final build action (junos_commit_config) fails when trying to move generated Junos config file from ``/root/.ansible/`` temporary working folder to ``/var/tmp/build/<hostname>/`` folder, which does not exist. Further investigation needed why sub-folders are not getting built. 
* Currently in order to get playbooks to run variables need to be manually loaded into AWX. While AWX loads the variable files under ``group_vars`` and ``hosts_vars`` folders as part of the project fetch, they are ignored. 
* Name resolution for hosts. NITA builds ``/etc/host`` file using shell scripts, need to find alternative for AWX EE environment. According to this https://github.com/ansible/awx/issues/1125 dynamically updating /etc/host file may not be feasible. In that case, we'd need to rely on external DNS resolution and/or manually updating k8s config files and restarting pod, which is not ideal. 



## AWX Screenshots

How the NITA example data is being loaded into AWX for testing (as of September 22, 2022).

### Template
![image](https://user-images.githubusercontent.com/6110061/191846632-018f1318-fa5a-4c45-99ee-7c4989afa1d6.png)

### Project

![image](https://user-images.githubusercontent.com/6110061/191846831-1f8644e1-96e2-496d-b77e-5a127d46ea61.png)

### Inventories

Note the variable data from ``groups_vars``

![image](https://user-images.githubusercontent.com/6110061/191847011-f2759976-4ef9-4eb4-ab93-0b4fbbb51673.png)

### Hosts

Each individual host has ``host_vars`` defined here 

![image](https://user-images.githubusercontent.com/6110061/191847136-9caa10a3-8e34-4c23-8c3b-60f88502c7cd.png)
![image](https://user-images.githubusercontent.com/6110061/191847262-1cefe0fa-5960-4513-8c06-a37247fa4aa3.png)




