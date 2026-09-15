# ********************************************************
#
# Project: nita-ansible
#
# Copyright (c) Juniper Networks, Inc., 2026. All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************

FROM alpine:3.23.3 AS builder

RUN apk add --no-cache \
    python3 py3-pip py3-virtualenv \
    gcc libxml2-dev libxslt-dev musl-dev python3-dev \
    libffi-dev openssl-dev build-base \
    bash ansible-core

WORKDIR /tmp
COPY requirements.txt requirements.txt
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
 && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
 && /opt/venv/bin/python -c "import jnpr.junos"

COPY requirements.yml requirements.yml
RUN ansible-galaxy collection install -r requirements.yml

COPY network-roles network-roles
RUN cd network-roles/ebgp-ip-fabric && bash install.sh \
 && cd /tmp/network-roles/evpn-vxlan-common && bash install.sh \
 && cd /tmp/network-roles/evpn-vxlan-fi && bash install.sh \
 && cd /tmp/network-roles/evpn-vxlan-erb && bash install.sh \
 && cd /tmp/network-roles/evpn-vxlan-hb && bash install.sh \
 && cd /tmp/network-roles/evpn-vxlan-sb && bash install.sh


FROM alpine:3.23.3

# ==> Specify Python requirements filename;   default = "requirements.txt"
# ==> Specify Ansible requirements filename;  default = "requirements.yml"
# ==> Specify playbook filename;              default = "playbook.yml"
# DO NOT CHANGE THESE DEFAULTS. OTHER APPS DEPEND ON THEM
ENV PYREQS="requirements.txt"
ENV REQUIREMENTS="requirements.yml"
ENV PLAYBOOK="playbook.yml"

RUN apk add --no-cache \
    sudo python3 \
    openssl ca-certificates git \
    bash openssh expect sshpass \
    curl vim \
    ansible-core ansible \
    libxml2 libxslt

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /root/.ansible /root/.ansible
COPY --from=builder /etc/ansible/roles /etc/ansible/roles

ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

WORKDIR /project
VOLUME /project

LABEL net.juniper.framework="NITA"

WORKDIR /root
CMD ["bash"]
