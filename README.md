[branch]: https://github.com/Juniper/nita/tree/23.12
[readme]: https://github.com/Juniper/nita/blob/23.12/README.md
[create_ansible_job_k8s]: https://github.com/Juniper/nita-jenkins/blob/23.12/create_ansible_job_k8s.py

# NITA Ansible 23.12

Welcome to NITA, an open source platform for automating the building and testing of complex networks.

# Release Notes
The major change in this version is that all components now run within pods under the control of Kubernetes, rather than as Docker containers. Consequently we have updated the way that Ansible runs because it is now controlled by Kubernetes instead of Docker. 

Please refer to the [README][readme] for more details.

# Installing

The simplest way to install nita-ansible is by installing the nita repositories, which can be done by running the ``install.sh`` script located and in the parent [nita repo][branch] as described [here][readme]. You can also install nita-ansible as a standalone Docker container, which can run independently of the NITA containers that are running under Kubernetes.

## Accessing the nita-ansible container

Note that the nita-ansible container is ephemeral, i.e. it is started and stopped by Jenkins when it is needed for a job. However, you can start an instance of a new Ansible container and access it via the shell simply be running the following command:

```
user@host$ nita-cmd ansible cli
If you don't see a command prompt, try pressing enter.
nita-ansible:~# exit
exit
pod "nita-ansible" deleted
user@host$
```

:warning: Unlike docker, many of the arguments needed by kubectl are defined in YAML files rather than being passed on the command line. For example, if you wish to mount a volume in a container from the host, you will need to define it in a YAML file. We use a python script ``create_ansible_job_k8s.py`` ([see link][create_ansible_job_k8s]) to create the required job_yaml, and you can use this as an example if you want to create your own ansible containers.

If you want to run a standalone Ansible container with your own playbooks and/or roles, we recommend doing so as a Docker container, described below.

# Running a Standalone Ansible Docker Container

We provide the ability for you to run Ansible as a standalone Docker container, without having to use the other parts of NITA that are controlled by Kubernetes, such as Jenkins, Robot Framework or the Webapp.  This is very handy if you want to be able to quickly just run an instance of Ansible with your own playbooks or roles, as is explained below.

## Ansible Versions: 2.10 and greater

Starting with Ansible 2.10, juniper.device and junipernetworks.junos ansible collections are available. This collection has been included in the requirements.yml file and will be built into the NITA container automatically. The existing juniper.junos role is still supported and works with Ansible 2.10. For more information on this transition see https://www.juniper.net/documentation/us/en/software/junos-ansible/ansible/topics/concept/junos-ansible-modules-overview.html and https://galaxy.ansible.com/juniper/device. Juniper.junos roles has been removed and are superceded by the newer collections. If the old roles are still required, simply uncomment the line from the standalone ``Dockerfile``:

```
RUN ansible-galaxy install Juniper.junos -p /etc/ansible/roles/
```

The network-roles that the Docker container copies over have been updated to remove the dependencies on the old roles and will use the collections.

## Using Standalone nita-ansible

This Docker container holds Ansible executables, related libraries, and files for managing Juniper devices using Ansible. The NITA framework uses the nita-ansible container to run ansible playbooks included with the framework. Nita-ansible can also be used as a standalone container for executing your own playbooks. Simply put your inventory file and playbooks into a new project folder on the system hosting the Docker container. You will also want to put a bash script to execute the ```ansible-playbook``` command.

### A Simple Project Folder Example

A simple project folder with a single playbook may look like this:

```
-rw-rw-r-- 1 auser auser  972 Jun  4 16:21 playbook.yml
-rw-rw-r-- 1 auser auser  148 Jun  4 10:42 hosts
-rwxrwxr-x 1 auser auser  136 Jun  4 16:22 runme.sh
```

The ```runme.sh``` should execute the playbook pointing to the hosts file as follows:

```
#!/bin/bash
ansible-playbook -i hosts playbook.yml
```
### Using Standalone nita-ansible with your project folder

To use the standalone nita-ansible Docker container with your project folder, simply use the ```docker run``` command, mounting your project folder onto the Docker container and passing the command to run your script like the example below:

```
docker run -u root -v /project_folder:/container_folder:rw  --rm  -it --name ansible juniper/nita-ansible:<version> /bin/bash -c "cd /container_folder; ./runme.sh"
```
### Troubleshooting playbooks

You can execute the playbook into a bash shell and troubleshoot from the project folder mounted inside the Docker container if your playbooks are not operating correctly by issuing the ```docker run``` command above with just the bash shell (remove everything after ```/bin/bash```).

## Built-in Ansible roles

Standalone nita-ansible contains many built-in roles for building Juniper configuration files related to an EVPN VXLAN IP fabric. An example of a project using these roles can be found at https://github.com/Juniper/nita-webapp/tree/main/examples/evpn_vxlan_erb_dc. When invoking the Docker container to use these roles an additional output directory needs to be mounted for the configuration files to be built and stored in the /container_build_folder (the example uses /var/tmp/build) folder as follows:

```
docker run -u root -v /project_folder:/container_folder:rw -v /local_output_folder:/container_build_folder --rm  -it --name ansible juniper/nita-ansible:<version> /bin/bash -c "cd /container_folder; ./runme.sh"
```

When invoking these built-in roles the build-folder needs to be passed to the ansible as a variable in the runme.sh file like this:

```
ansible-playbook -i hosts playbook.yaml --extra-vars "build_dir=container_build_folder"
```
### ebgp_ip_fabric

Builds the configuration stanzas that make up a Junos eBGP IP fabric underlay. It includes configurations for forwarding, routing, and policy options as well as interfaces participating in the fabric and BGP protocol configuration. In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information include "underlay_ebgp+", "core_interfaces+", "underlay_ebgp+"

Invoking this role from ansible playbook can be accomplished as follows:
```
- hosts: switches
  connection: local
  roles:
    - { role: junos_qfx_common }
    - { role: ebgp_ip_fabric }
```

### evpn_vxlan_common

Builds the configuration stanzas that make up a Junos policy and routing options for leaf nodes. It also checks the leaf_type variable and if it is type "border" will create the policy to export default routes via both EVPN and OSPF. Invoking this role from an ansible playbook can be accomplished as follows:
```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_common }
```

Included in the evpn_vxlan_common role is <b>junos_commit_config</b> role which includes examples for using juniper.junos roles (commented out) and juniper.device collection (see <b>ansible 2.10 and greater</b> above)

### evpn_vxlan_dci

Builds the configuration stanzas that make up a eBGP routing for DCI connectivity. In the sample Excel file included with the NITA package for EVPN data center, the tab that holds the variable is "dci_ebgp+". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_dci }
```

### evpn_vxlan_erb_leaf

Builds the configuration stanzas that make up iBGP EVPN overlay configuration for leafs in spine/leaf IP fabric. Also includes configuration for related switch-options stanza in Junos (vtep source interface, route-distinguisher, vrf-target).
In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information include "evpn_ibgp+" and "base". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_erb_leaf }
```

### evpn_vxlan_erb_spine

Builds the configuration stanzas that make up iBGP EVPN overlay "lean" spines as iBGP route-reflectors for family evpn signaling. Of particular interest the configuration implicitly allows all neighbors from the defined loopback_subnet. This means all the leafs will initiate the BGP connection.
In the sample Excel file included with the NITA package for EVPN data center,  the tabs that hold the variable information include "evpn_ibgp+" and "base". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: spines
  connection: local
  roles:
    - { role: evpn_vxlan_erb_spine }
```

### evpn_vxlan_port

Builds the configuration stanzas that make up L2 port information for devices connected to leafs in an EVPN VXLAN IP Fabric. Configures ports, ESIs, VLANs, LAGs, and IP addresses. In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information include "evpn_port+" and "base". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_port }
```

### evpn_vxlan_vni

Builds the configuration stanzas that make up VNI information for EVPN VXLAN configuration.
In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information include "vnis+". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_vni }
```

### evpn_vxlan_vrf

Builds the configuration stanzas that make up VRF for EVPN VXLAN configuration. In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information include "vrfs+" (and indirectly "vnis+". The example datacenter uses route-targets and does not create unique policies for each VRF. Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_vrf }
```

### Junos_common

Builds the configuration stanzas that make that includes configuration stanzas common to all junos devices. Configures ethernet device aggregation in chassis, grpc under system services, management interface (will configure DHCP if no IP address is assigned), static routes under routing-options, and snmp. It is invoked:

```
- hosts: switches
  pre_tasks:
  connection: local
  roles:
    - { role: junos_common }
```

### junos_qfx_common

This includes the configuration templates for the base Junos config portion of a QFX switch. In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information related to this role include "base" and "password_hashes".

Invoking this role from ansible playbook can be accomplished as follows:

```
- hosts: switches
  connection: local
  roles:
    - { role: junos_qfx_common }
```

### srx_common and srx_firewall

This includes the configuration templates for the base Junos config portion of an switch. In the sample Excel file included with the NITA package for EVPN data center, the tabs that hold the variable information related to this role include "base", "password_hashes", "vrfs+", and "firewall_port+".

Invoking this role from ansible playbook can be accomplished as follows:

```
- hosts: firewalls
  pre_tasks:
  connection: local
  roles:
    - { role: junos_common }
    - { role: srx_common }
    - { role: srx_firewall }
```

### junos_commit_config

Once the device configuration files have been built and stored in the build folder, this role will manually commit the configuration files to their respective Junos device. Invokes as follows:

```
- hosts: all
  connection: local
  gather_facts: no
  roles:
    - { role: junos_commit_config }
```

## Additional roles

If you need additional roles for your playbooks, create a folder in project directory called ```roles``` and copy the appropriate files from your local ansible installation's role folder. Ansible will look in ```/container_folder/roles``` for any roles that are not already installed in the Docker container itself.

## mx_common

This role is not actually included in the default container build but is an example of a role that can be added via the project. This role is located at https://github.com/Juniper/nita-webapp/tree/main/examples/ebgp_wan and NITA loads it under the roles folder in the project folder.

This role contains junos configuration statements for the MX router in the WAN role in the NITA example project.

## Examples

More complex examples of project folders can be found in the larger NITA project itself, particularly at https://github.com/Juniper/nita/tree/main/examples.

# Copyright

Copyright 2024, Juniper Networks, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
