# ********************************************************
#
# Project: nita-ansible
# Version: 20.10
#
# Copyright (c) Juniper Networks, Inc., 2020. All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************

FROM ansible/ansible-runner:1.4.6

WORKDIR /tmp

# Copy and install Python3 library and modules dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

#Copy and install Ansible module and collections dependencies
COPY requirements.yml .
RUN ansible-galaxy role install -r requirements.yml
RUN ansible-galaxy collection install -r requirements.yml

COPY roles.tar.gz .
RUN tar -zxvf roles.tar.gz
RUN cd ebgp-ip-fabric && bash install.sh
RUN cd evpn-vxlan-common && bash install.sh
RUN cd evpn-vxlan-dci && bash install.sh
RUN cd evpn-vxlan-erb && bash install.sh
RUN cd evpn-vxlan-hb && bash install.sh
RUN cd evpn-vxlan-sb && bash install.sh

LABEL net.juniper.framework="NITA"

WORKDIR /runner
