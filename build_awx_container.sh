#!/bin/bash
# ********************************************************
#
# Project: nita-awx
#
# Copyright (c) Juniper Networks, Inc., 2022. All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************
cd nita-awx
git clone https://github.com/ansible/awx-operator.git
export NAMESPACE=awx
kubectl create ns $NAMESPACE
sudo kubectl config set-context --current --namespace=$NAMESPACE
kubectl get pods
cd awx-operator
git checkout 2.1.0
make deploy
kubectl get pods
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: static-data-pvc
  namespace: awx
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 5Gi
EOF
cp ../awx-deploy.yml .
kubectl apply -f awx-deploy.yml
echo "Waiting for AWX containers. Launching watch command (ctrl-c when pods after verifying pod are running)"
sleep 20
watch kubectl get pods -l "app.kubernetes.io/managed-by=awx-operator"
echo -e "\nGetting service information using"
kubectl get svc -l "app.kubernetes.io/managed-by=awx-operator"
