# ********************************************************
#
# Project: nita-ansible
#
# Copyright (c) Juniper Networks, Inc., 2021. All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************

FROM alpine:3.12.1

# ==> Specify Python requirements filename;   default = "requirements.txt"
# ==> Specify Ansible requirements filename;  default = "requirements.yml"
# ==> Specify playbook filename;              default = "playbook.yml"
# DO NOT CHANGE THESE DEFAULTS. OTHER APPS DEPEND ON THEM
ENV PYREQS="requirements.txt"
ENV REQUIREMENTS="requirements.yml"
ENV PLAYBOOK="playbook.yml"

RUN apk add --no-cache sudo \
    python3 py3-pip openssl ca-certificates git \
    gcc libxml2-dev libxslt-dev musl-dev \
    bash python3-dev openssh expect sshpass \
    libffi-dev openssl-dev build-base curl \
    ansible=2.9.18-r0 vim

# copy requirements.txt for Python and install
WORKDIR /tmp
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN ansible-galaxy install Juniper.junos -p /etc/ansible/roles/
COPY requirements.yml .
RUN ansible-galaxy collection install -r requirements.yml

COPY network-roles network-roles
RUN cd network-roles/ebgp-ip-fabric && bash install.sh
RUN cd network-roles/evpn-vxlan-common && bash install.sh
RUN cd network-roles/evpn-vxlan-fi && bash install.sh
RUN cd network-roles/evpn-vxlan-erb && bash install.sh
RUN cd network-roles/evpn-vxlan-hb && bash install.sh
RUN cd network-roles/evpn-vxlan-sb && bash install.sh

WORKDIR /project
VOLUME /project

LABEL net.juniper.framework="NITA"

WORKDIR /root
CMD bash
