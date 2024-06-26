<H1> AWX Execution Environment </H1>

Files located in this directory are used to create ansible execution environment for AWX/Ansible Tower. the ```build-ee-container.sh``` script calls ansible-builder, which needs to be installed using pip (see https://ansible-builder.readthedocs.io/en/stable/installation/). Ansible-builder requires python3.8 or later to execute. [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) and [Docker](https://docs.docker.com/engine/install/ubuntu/) also need to be installed. 

AWX requires ansible EEs to be pulled from a repository. For testing purposes you can setup a local repository. See the instructions at https://www.docker.com/blog/how-to-use-your-own-registry-2/. After building the container, you can add a local repository as follows:

```
docker run -d -p 5000:5000 --restart always --name registry registry
docker tag <Ansible-ee-container-image-id> "localhost:5000/nita-ansible-ee"
docker push localhost:5000/nita-ansible-ee
```

After this simply define the localhost:5000/ansible-ee in your definition for an Execution Environment in AWX:

<img width="1510" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/4e61b9ba-f107-4b6e-9dd9-965264178554">


<H2> Notes </H2>

+ This container is being tested against a version of the ebgp-wan example from the NITA project. Current files for the AWX test version can be found at https://github.com/wildsubnet/awx-test. The AWX installation included here creates a folder called /data/project that will be mounted in the AWX Task container under /var/lib/awx/projects. For the NITA WAN demo you can ``git clone https://github.com/wildsubnet/awx-test`` awx-test under your actual project folder. 

## AWX Screenshots

How the NITA example data is being loaded into AWX for testing.

### Template
<img width="1526" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/5820f15e-a9ff-44c9-b48b-d209b5ca6923">


### Project

<img width="1505" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/de5572ab-6707-415a-94e0-f9d8765dee99">


### Inventories

Note the variable data from ``groups_vars``. Also AWX requires an additional variable definition here ``ansible_python_interpreter: "{{ ansible_playbook_python }}"`` otherwise it will toss a missing module error because it runs the wrong python environment. See [this](https://www.reddit.com/r/ansible/comments/rb80pv/execution_environments_and_pip_module_locations/) thread.

<img width="1269" alt="image" src="https://github.com/wildsubnet/nita-awx/assets/6110061/958f3a4e-c262-4c8d-b92a-b1d56ea40204">

### Hosts

Each individual host has ``host_vars`` defined here 

<img width="1277" alt="image" src="https://user-images.githubusercontent.com/6110061/235500135-b8bf91ca-a3f5-49a4-a625-a5820bba60e4.png">
<img width="1277" alt="image" src="https://user-images.githubusercontent.com/6110061/191847262-1cefe0fa-5960-4513-8c06-a37247fa4aa3.png">
