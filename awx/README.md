# nita-awx

This is being used to test the AWX execution environment. AWX requires kubernetes.

## Folders

<b>ansible-ee</b> - setup files to build ansible execution environment based on https://github.com/juniper/nita-ansible container.


## Installation

1. Install Kubernetes. The build script assumes kubernetes is already installed. 

2. Install AWX using the provided script as show below. This does a few things in addition to pulling a specific version of AWX. The script creates a namespace in k8s called ```awx```. It also creates the pods required to run AWX and spins up a service running on default ports for AWX. 

```
cd nita-ansible
./build_awx_container.sh
```

3. After install AWX, you will need to retrieve the admin password to login into the AWX console.

```
kubectl -n awx get secret  awx-admin-password -o jsonpath="{.data.password}" | base64 --decode
```

4. Login into the webconsole at localhost:31768 and change the user password (if desired) with username admin and the password decoded above. 

<img width="1502" alt="image" src="https://github.com/wildsubnet/nita-ansible/assets/6110061/fca0a3b0-d75e-480d-8fd1-38d982799fcd">

5. Setup execution environment for NITA.

See [ansible-ee/README.md](ansible-ee/README.md) for details.

## Coming Soon

NITA has been ported to k8s so we can being integration work with AWX.  
