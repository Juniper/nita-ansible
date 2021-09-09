# NITA Ansible 21.7

Welcome to NITA 21.7.

Packages built from this branch will be nita-*-21.7-x where x is the packaging release.
This branch also contains patches from other branches or minor modifications as required to support the stability and usability of the release.
There are also some backwards compatibility packages here for ansible and robot that allow projects written for NITA 3.0.7 to work without having to make any changes.

Note that NITA 21.7 is backward compatible with NITA 20.10 projects, provided the correct ansible and robot containers are installed.

# Copyright

Copyright 2021, Juniper Networks, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Stable releases

The idea here is to provide multiple NITA based projects with a firm foundation that they can use to focus on solving customer problems rather than continually tweaking the underlying software.

It allows NITA projects to declare exactly which version of NITA they are compatible with.

Projects must explicitly use the versions of the containers provided by this package in order to avoid docker attempting to download from the registry.
No containers tagged as "latest" are provided by the package.

# Installing

## Dependencies

NITA depends on docker-ce and docker-compose.

* For the **docker-ce** installation the instructions found here: https://docs.docker.com/engine/install/
* It is recommended to follow this steps after installing docker-ce: https://docs.docker.com/engine/install/linux-postinstall/
* To install **docker-compose** follow the instructions found here: https://docs.docker.com/compose/install/

## Installation

If you do not have the the required package files for your system, .deb for Ubuntu or .rpm for Centos refer to [BUILD.md](./BUILD.md) file for instructions on how to generate them.

### Ubuntu

If you have been provided with the .deb package file, then follow the instructions provided in the [Dependencies](##Dependencies) section above and then run the following command:

```bash
sudo apt-get install ./nita-ansible-2.9.18-21.7-1.deb
```

### Centos

If you have been provided with the .rpm package file, then follow the instructions provided in the [Dependencies](##Dependencies) section above and then run the following command:


```bash
sudo yum install ./nita-ansible-2.9.18-21.7-1.noarch.rpm
```
# Using nita-ansible

This container holds Ansible executables, related libraries, and files for managing Juniper devices using Ansible. The NITA framework uses the nita-ansible container to run ansible playbooks included with the framework. Nita-ansible can also be used as a standalone container for executing your own playbooks. Simply put your inventory file and playbooks into a project folder on the system hosting the container. You will also want to put a bash script to execute the ```ansible-playbook``` command.

### Simple Project Folder Example

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

### Using nita-ansible with your project folder

To use the nita-ansible container with your project folder, simply use the ```docker run``` command, mounting your project folder onto the container and passing the command to run your script like the example below:

```
docker run -u root -v /project_folder:/container_folder:rw  --rm  -it --name ansible juniper/nita-ansible:<version> /bin/bash -c "cd /container_folder; ./runme.sh"
```

### Troubleshooting playbooks

You can execute the playbook into a bash shell and troubleshoot from the project folder mounted inside the container if your playbooks are not operating correctly by issuing the ```docker run``` command above with just the bash shell (remove everything after ```/bin/bash```).

# Roles

## Built-in roles

This container contains many built-in roles for building Juniper configuration files related to an EVPN VXLAN IP fabric. An example of a project using these roles can be found at https://github.com/Juniper/nita-webapp/tree/main/examples/evpn_vxlan_erb_dc. When invoking the container to use these roles an additional output directory needs to be mounted for the configuration files to be built and stored in the /container_build_folder (the example uses /var/tmp/build) folder as follows:

```
docker run -u root -v /project_folder:/container_folder:rw -v /local_output_folder:/container_build_folder --rm  -it --name ansible juniper/nita-ansible:<version> /bin/bash -c "cd /container_folder; ./runme.sh"
```

When invoking these built-in roles the build-folder needs to be passed to the ansible as a variable in the runme.sh file like this:

```
ansible-playbook -i hosts playbook.yaml --extra-vars "build_dir=container_build_folder"
```

### Juniper.junos

This is the main Junos Ansible 2.9 role and is included in the nita-ansible container. This role allows Ansible to communicate with Junos devices. Information on the functionality that is provided with this Ansible role can found here: https://www.juniper.net/documentation/en_US/junos-ansible/topics/reference/general/junos-ansible-modules-overview.html

### ebgp_ip_fabric

Builds the configuration stanzas that make up a Junos eBGP IP fabric underlay. It includes configurations for forwarding, routing, and policy options as well as interfaces participating in the fabric and BGP protocol configuration. In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information include "underlay_ebgp+", "core_interfaces+", "underlay_ebgp+"

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

### evpn_vxlan_dci

Builds the configuration stanzas that make up a eBGP routing for DCI connectivity. In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tab that holds the variable is "dci_ebgp+". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_dci }
```

### evpn_vxlan_erb_leaf

Builds the configuration stanzas that make up iBGP EVPN overlay configuration for leafs in spine/leaf IP fabric. Also includes configuration for related switch-options stanza in Junos (vtep source interface, route-distinguisher, vrf-target).
In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information include "evpn_ibgp+" and "base". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_erb_leaf }
```

### evpn_vxlan_erb_spine

Builds the configuration stanzas that make up iBGP EVPN overlay "lean" spines as iBGP route-reflectors for family evpn signaling. Of particular interest the configuration implicitly allows all neighbors from the defined loopback_subnet. This means all the leafs will initiate the BGP connection.
In the sample Excel file included with the NITA package for EVPN data center mentioned above,  the tabs that hold the variable information include "evpn_ibgp+" and "base". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: spines
  connection: local
  roles:
    - { role: evpn_vxlan_erb_spine }
```

### evpn_vxlan_port

Builds the configuration stanzas that make up L2 port information for devices connected to leafs in an EVPN VXLAN IP Fabric. Configures ports, ESIs, VLANs, LAGs, and IP addresses. In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information include "evpn_port+" and "base". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_port }
```

### evpn_vxlan_vni

Builds the configuration stanzas that make up VNI information for EVPN VXLAN configuration.
In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information include "vnis+". Invoking this role from an ansible playbook can be accomplished as follows:

```
- hosts: leaves
  connection: local
  roles:
    - { role: evpn_vxlan_vni }
```

### evpn_vxlan_vrf

Builds the configuration stanzas that make up VRF for EVPN VXLAN configuration. In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information include "vrfs+" (and indirectly "vnis+". The example datacenter uses route-targets and does not create unique policies for each VRF. Invoking this role from an ansible playbook can be accomplished as follows:

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

This includes the configuration templates for the base Junos config portion of a QFX switch. In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information related to this role include "base" and "password_hashes".

Invoking this role from ansible playbook can be accomplished as follows:

```
- hosts: switches
  connection: local
  roles:
    - { role: junos_qfx_common }
```

### srx_common and srx_firewall

This includes the configuration templates for the base Junos config portion of an switch. In the sample Excel file included with the NITA package for EVPN data center mentioned above, the tabs that hold the variable information related to this role include "base", "password_hashes", "vrfs+", and "firewall_port+".

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

If you need additional roles for your playbooks, create a folder in project directory called ```roles``` and copy the appropriate files from your local ansible installation's role folder. Ansible will look in ```/container_folder/roles``` for any roles that are not already installed in the container itself.

## mx_common

This role is not actually included in the default container build but is an example of a role that can be added via the project. This role is located at https://github.com/Juniper/nita-webapp/tree/main/examples/ebgp_wan and NITA loads it under the roles folder in the project folder.

This role contains junos configuration statements for the MX router in the WAN role in the NITA example project.

# Examples

More complex examples of project folders can be found in the larger NITA project itself, particularly at https://github.com/Juniper/nita-webapp/tree/main/examples

# Misc

For more information on NITA releases refer to the [README.md](https://github.com/Juniper/nita-webapp/blob/21.7/README.md) for the NITA Webapp.
