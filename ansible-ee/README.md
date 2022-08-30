Files located in this directory are used to create ansible execution environment for AWX/Ansible Tower. the ```build-container.sh``` script calls ansible-builder, which needs to be installed using pip (see https://ansible-builder.readthedocs.io/en/stable/installation/). Ansible-builder requires python3.8 or later to execute. You can also build the container directly by issuing the following commands:

```
cd context
docker build  --tag "juniper/nita-ansible-ee:22.9" .
```

AWX requires ansible EEs to be pulled from a repository. For testing purposes you can setup a local repository. See the instructions at https://www.docker.com/blog/how-to-use-your-own-registry-2/. After building the container, you can add a local repository as follows:

```
docker run -d -p 5000:5000 --restart always --name registry registry
docker tag <Ansible-ee-container-image-id> "localhost:5000/ansible-ee"
docker push localhost:5000/ansible-ee
```
