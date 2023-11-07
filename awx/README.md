# nita-awx

This is being used to test the AWX execution environment. AWX requires kubernetes.

## Folders

<b>ansible-ee</b> - setup files to build ansible execution environment based on https://github.com/juniper/nita-ansible container.


## Installation

1. Install Kubernetes. The build script assumes kubernetes is already installed. K3s (https://k3s.io/) was used to test this installation procedure. To install k3s issue the following commands:
```
curl -sfL https://get.k3s.io | sudo bash - 
sudo chmod 644 /etc/rancher/k3s/k3s.yaml 
```

You can test the installation of k3s with the following commands:
```
kubectl get nodes
kubectl version --short
```

Note: k8s is less forgiving of implied storage requirements and may require additional storage setup for AWX to start properly.

2. Install AWX using the provided script as show below. This does a few things in addition to pulling a specific version of AWX. The script creates a namespace in k8s called ```awx```. It also creates the pods required to run AWX and spins up a service running on default ports for AWX. 

```
cd nita-awx
./build_container.sh
```

3. After installing AWX, you should create a superuser. This can be done by initiating a bash shell on the awx-web pod and executing the appropriate command (follow the prompts):

```
kubectl exec -ti deploy/awx -c awx-web -- "/bin/bash"
bash-5.1$ awx-manage createsuperuser
```

4. Finally you will need an ansible execution environment. 

```
cd ansible-ee
./build_container.sh
```

See [ansible-ee/README.md](ansible-ee/README.md) for details.

## Updating

In order to update versions of AWX, simply run the following commands and re-run the installation script:

```
kubectl delete deployment awx-operator-controller-manager
kubectl delete serviceaccount awx-operator-controller-manager
kubectl delete rolebinding awx-operator-awx-manager-rolebinding
kubectl delete role awx-operator-awx-manager-role
```

 ## To-do

Need to update installer for k8s rather than k3s and still need integration between nita webapp and AWX.

