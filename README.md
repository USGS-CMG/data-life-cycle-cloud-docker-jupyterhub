# JupyterHub Dockr Swarm service

## Introduction

[JupyterHub](https://jupyterhub.readthedocs.io/en/latest/) is a multi-user hub that
may be run in a clustered container configuration. The approach taken in this project
is to run the JupyterHub cluster using Docker Swarm. The JupyterHub server runs on
a manager node. For each new user that logs in, JupyterHub will launch a new Docker
Swarm service of one Docker container that is an isolated [Jupyter notebook server](https://jupyter-notebook.readthedocs.io/en/latest/).
To do so, the JupyterHub Docker container actually has a Docker client installed on it.
This Docker client communicates to the Docker Engine running on the node that it sits
on. Because the JupyterHub service runs on the manager node, JupyterHub is able to
control the Docker Swarm manager in order to have it spawn and remove Jupyter Notebook
services as needed.

Each user that logs in also gets a Docker Volume associated with that user. The volume
persists so that the user's work is not lost each time they log out. The volumes may
be pruned manually.

This project uses the community [JupyterHub Docker container](https://hub.docker.com/r/jupyterhub/jupyterhub/).

This project is meant to run in a production Docker Swarm cluster in a cloud environment.

*This project is still a work in progress.*

## Docker Software Versions

For testing this configuration, I have the following software installed at these versions:

- Docker Machine: 0.12.10
- Docker Compose: 1.15.0
- Docker Client: 17.06.0-ce

## Creating a local Docker Swarm cluster

To run the project locally, a developer will need to set up a running Docker Swarm
cluster along with a Docker private registry service running in that cluster. Information on how to do so can be found [here](https://github.com/USGS-CMG/data-life-cycle-cloud/blob/f75f79f94e16497536e919ff07eaaddd78a1353d/docker/README.md#creating-a-local-swarm-cluster-tldr).
(Skip to the [tl;dr](https://github.com/USGS-CMG/data-life-cycle-cloud/blob/f75f79f94e16497536e919ff07eaaddd78a1353d/docker/README.md#swarm-create-tldr))
to get up and running in a few minutes.

## Building the JupyterHub and Jupyter Notebook Docker containers

To test locally, you will need to build the JupyterHub and Jupyter Notebook Docker
containers and deploy them to your locally running private registry. Doing so allows
Docker Swarm to use the private registry to pull the JupyterHub and Jupyter Notebook
images to deploy as services to the swarm.

Assuming that your currently working directory is the root of this project, first
build the JupyterHub Docker container. This also assumes that your local Docker client is set to communicate to any
of the Docker Machine VMs by the use of the `eval $(docker-machine env $MACHINE_NAME)`
command. That step is part of the setup in getting the Swarm cluster going.

```
$ docker build -t localhost:5000/dlcc/jupyterhub:latest ./files/jupyterhub/
Building jupyterhub
Step 1/14 : FROM jupyterhub/jupyterhub:0.7.2
0.7.2: Pulling from jupyterhub/jupyterhub
75a822cd7888: Pull complete
0a42d45e721b: Pull complete
63589f40d684: Pull complete
99690b19de93: Pull complete
e6155012c1c9: Pull complete
53546243fe6b: Pull complete
Digest: sha256:9b2b7642fc73f20482e1557ea63820c4f7949689c6cefded41b2ac56bca4d752
Status: Downloaded newer image for jupyterhub/jupyterhub:0.7.2
---> c74ccf481090
Step 2/14 : MAINTAINER Ivan Suftin <isuftin@usgs.gov>

[...]

Removing intermediate container 16497a7abee2
Step 13/14 : RUN chmod +x /srv/jupyterhub/entrypoint.sh
 ---> Running in f4cb744c3efa
 ---> 3c31677c3004
Removing intermediate container f4cb744c3efa
Step 14/14 : ENTRYPOINT /srv/jupyterhub/entrypoint.sh &&
 ---> Running in 369adb5b8686
 ---> ad08e9525401
Removing intermediate container 369adb5b8686

Successfully built ad08e9525401
Successfully tagged localhost:5000/dlcc/jupyterhub:latest
```

Notice that the resulting image is named `localhost:5000/dlcc/jupyterhub:latest`.
That URL happens to be the URL of your private Docker registry which *should* be
currently running as a service within your Docker Swarm. So now you should just be
able to push that built image to your registry.

```
$  docker push localhost:5000/dlcc/jupyterhub:latest
The push refers to a repository [localhost:5000/dlcc/jupyterhub]
9e914f4c4596: Pushed
3873c961a7fe: Pushed

[...]

b944bcd9b3b6: Pushed
b6ca02dfe5e6: Pushed
latest: digest: sha256:bafebdc7969dbfa1db2cc71c173db6c097d73ea08f7127fa7a4e3054c498902d size: 3879
```

Building the Jupyter Notebook container works about the same. The only difference
is the location of the Dockerfile

```
$ docker build -t localhost:5000/dlcc/jupyter-singleuser:latest files/jupyter-docker-stacks/single-user/
Sending build context to Docker daemon  2.048kB
Step 1/3 : FROM jupyter/scipy-notebook
latest: Pulling from jupyter/scipy-notebook
e0a742c2abfd: Pull complete
486cb8339a27: Pull complete

[...]

bbf3524fd783: Pull complete
a5099f223a85: Pull complete
Digest: sha256:e4c98e1a246743c03efe4508110b9e755f73b85758b988e779ef61d8ac881632
Status: Downloaded newer image for jupyter/scipy-notebook:latest
 ---> 092599e85093
Step 2/3 : MAINTAINER Ivan Suftin <isuftin@usgs.gov>
 ---> Running in 792e0cb3360b
 ---> b71d49b97299
Removing intermediate container 792e0cb3360b
Step 3/3 : CMD /usr/local/bin/start-singleuser.sh
 ---> Running in 3bf48fb9f3dc
 ---> 092aa5b3f82e
Removing intermediate container 3bf48fb9f3dc
Successfully built 092aa5b3f82e
Successfully tagged localhost:5000/dlcc/jupyter-singleuser:latest

docker push  localhost:5000/dlcc/jupyter-singleuser:latest
The push refers to a repository [localhost:5000/dlcc/jupyter-singleuser]
1308a6f868a5: Pushed
df9237f6a830: Pushed

[...]

aca233ed29c3: Pushed
e5d2f035d7a4: Pushed
latest: digest: sha256:dc80e9eb59472c18ce458f1d7a85e893d50b038b0117dcaefb90c1a146fb7c28 size: 4916
$
```

Now the locally built images are available for any Swarm node to use as a
service from your private registry.

```
$ docker-machine ssh manager curl -s 'http://localhost:5000/v2/_catalog'
{"repositories":["dlcc/jupyter-singleuser","dlcc/jupyterhub"]}
$ docker-machine ssh manager curl -s 'http://localhost:5000/v2/dlcc/jupyterhub/tags/list'
{"name":"dlcc/jupyterhub","tags":["latest"]}
$ docker-machine ssh manager curl -s 'http://localhost:5000/v2/dlcc/jupyter-singleuser/tags/list'
{"name":"dlcc/jupyter-singleuser","tags":["latest"]}
```
