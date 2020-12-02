#!/bin/bash
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

[ -d ebgp-ip-fabric ] || git clone https://github.com/JNPRAutomate/ebgp-ip-fabric.git
[ -d evpn-vxlan-common ] || git clone https://github.com/JNPRAutomate/evpn-vxlan-common.git
[ -d evpn-vxlan-fi ] || git clone https://github.com/JNPRAutomate/evpn-vxlan-fi.git
[ -d evpn-vxlan-erb ] || git clone https://github.com/JNPRAutomate/evpn-vxlan-erb.git
[ -d evpn-vxlan-hb ] || git clone https://github.com/JNPRAutomate/evpn-vxlan-hb.git
[ -d evpn-vxlan-sb ] || git clone https://github.com/JNPRAutomate/evpn-vxlan-sb.git
tar -zcvf roles.tar.gz ebgp-ip-fabric evpn-vxlan-common evpn-vxlan-fi evpn-vxlan-erb evpn-vxlan-hb evpn-vxlan-sb

docker build -t juniper/nita-ansible:20.10-1 .
