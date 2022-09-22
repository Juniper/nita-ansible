ARG EE_BASE_IMAGE=quay.io/ansible/ansible-runner:latest
ARG EE_BUILDER_IMAGE=quay.io/ansible/ansible-builder:latest

FROM $EE_BASE_IMAGE as galaxy
ARG ANSIBLE_GALAXY_CLI_COLLECTION_OPTS=-vvv
USER root

ADD _build /build
WORKDIR /build

RUN ansible-galaxy role install -r requirements.yml --roles-path "/usr/share/ansible/roles"
RUN ANSIBLE_GALAXY_DISABLE_GPG_VERIFY=1 ansible-galaxy collection install $ANSIBLE_GALAXY_CLI_COLLECTION_OPTS -r requirements.yml --collections-path "/usr/share/ansible/collections"

FROM $EE_BUILDER_IMAGE as builder

COPY --from=galaxy /usr/share/ansible /usr/share/ansible

ADD _build/requirements.txt requirements.txt
ADD _build/bindep.txt bindep.txt
RUN ansible-builder introspect --sanitize --user-pip=requirements.txt --user-bindep=bindep.txt --write-bindep=/tmp/src/bindep.txt --write-pip=/tmp/src/requirements.txt
RUN assemble

FROM $EE_BASE_IMAGE
USER root
RUN whoami
RUN cat /etc/os-release

COPY --from=galaxy /usr/share/ansible /usr/share/ansible

COPY --from=builder /output/ /output/
RUN /output/install-from-bindep && rm -rf /output/wheels
COPY network-roles network-roles
RUN cd network-roles/ebgp-ip-fabric && bash install.sh
RUN cd network-roles/evpn-vxlan-common && bash install.sh
RUN cd network-roles/evpn-vxlan-fi && bash install.sh
RUN cd network-roles/evpn-vxlan-erb && bash install.sh
RUN cd network-roles/evpn-vxlan-hb && bash install.sh
RUN cd network-roles/evpn-vxlan-sb && bash install.sh
COPY network-roles/mx_common/ /etc/ansible/roles/mx_common
RUN mkdir -p /var/nita_configs
RUN mkdir -p /var/tmp/build
