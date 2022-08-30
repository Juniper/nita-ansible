Files located in this directory are used to create ansible execution environment for AWX/Ansible Tower. the ```build-container.sh``` script calls ansible-builder, which needs to be installed using pip (see https://ansible-builder.readthedocs.io/en/stable/installation/). Ansible-builder requires python3.8 or later to execute. You can also build the container directly by issuing the following commands:

```
cd context
docker build  --tag "juniper/nita-ansible-ee:22.9" .
```
