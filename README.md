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

## Building the JupyterHub and Jupyter Notebook Docker containers ([tl;dr](#building-jupyter-tldr))

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

$ docker push  localhost:5000/dlcc/jupyter-singleuser:latest
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

### <a name="building-jupyter-tldr"></a>Building Jupyter Docker images tl;dr

This tl;dr assumes your current working directory is the root of this project and
you're running the Docker private registry in your [Docker Swarm](https://github.com/USGS-CMG/data-life-cycle-cloud/blob/f75f79f94e16497536e919ff07eaaddd78a1353d/docker/README.md#creating-a-local-swarm-cluster-tldr)
on Docker Machine.

```
docker build -t localhost:5000/dlcc/jupyterhub:latest ./files/jupyterhub/
docker push localhost:5000/dlcc/jupyterhub:latest
docker build -t localhost:5000/dlcc/jupyter-singleuser:latest ./files/jupyter-docker-stacks/single-user/
docker push  localhost:5000/dlcc/jupyter-singleuser:latest
```

## Running JupyterHub

Now that you have the Docker images in your local registry, you are ready to deploy
them to your locally running Swarm cluster.

### Configuration

JupyterHub's primary configuration file is located in this project under `files/jupyterhub/jupyterhub_config.py`.
This file is copied into the JupyterHub Docker container when it is deployed into
a stack. If you want, you should feel free to change this file. More Information
about this file [may be found in the JupyterHub documentation](http://jupyterhub.readthedocs.io/en/latest/getting-started/config-basics.html).  

When launching the JupyterHub Swarm stack via the Docker Compose configuration
using `docker stack deploy`, there is an environment file that is used to provide
further configuration to the running JupyterHub service.  The file used by default
is `files/jupyterhub/compose.env`.

This file sets environment variables into a running container that JupyterHub uses
during initialization.  You can either edit this file directly or you can duplicate
this file to a file named (for example) `compose_local.env`. You can then use this
new file to set your own configuration. In order for Docker to pick up your new file,
before launching a stack you must set an environment variable named `DOCKER_JUPYTERHUB_LOCAL_ENV`
to `_local`. In doing so, Docker will read from the file `compose_local.env` instead.

This isn't mandatory but in doing so, you will not incur conflicts when pulling down
the latest changes for this project from version control.

### SSL Configuration

When running JupyterHub in production, you may (should) want to use SSL. There
are self-signed SSL certificates included with this project as an example of how
they are used on a running server. The SSL certificates are placed into
`files/jupyterhub/ssl/`. They are named jupyterhub_ssl_cert.crt and jupyterhub_ssl_key.pem.

When the JupyterHub server starts, those files are copied into the running container
to the locations `/srv/jupyterhub/ssl/jupyterhub_ssl_key.pem` and `/srv/jupyterhub/ssl/jupyterhub_ssl_cert.crt`.
They are picked up by the `jupyterhub_config.py` file and used for encryption.

### Secret Cookie File

JupyterHub uses a [cookie secret](http://jupyterhub.readthedocs.io/en/latest/getting-started/security-basics.html?highlight=cookie#cookie-secret)
that is used to encrypt browser cookies used for authentication. A default file
is included with this project at `files/jupyterhub/jupyterhub_cookie_secret`. In
production, you should set this to your own value. To do so, you may edit this file
directly or create a  `files/jupyterhub/jupyterhub_cookie_secret_local` file and
enter your own value there. Make sure to set your environment variable `DOCKER_JUPYTERHUB_LOCAL_ENV`
to `_local` if doing so.

### Auth Token Configuration

JupyterHub and the notebook proxies use a [proxy auth token](http://jupyterhub.readthedocs.io/en/latest/getting-started/security-basics.html?highlight=cookie#authentication-token)
to communicate. A default file is included with this project at
`files/jupyterhub/jupyterhub_proxy_auth_token`. In production, you should set
this to your own value. To do so, you may edit this file directly or create a  
`files/jupyterhub/jupyterhub_proxy_auth_token` file and enter your own value there.
Make sure to set your environment variable `DOCKER_JUPYTERHUB_LOCAL_ENV` to `_local`
if doing so.

####  Logging in

##### Local users

JupyterHub has a [number of different authenticators](https://github.com/jupyterhub/jupyterhub#authenticators)
that can be used as a login mechanism. By default, JupyterHub uses the PAMAuthenticator
module. There is a user initially created for this module named "testuser".
The password is "testpassword". You can add more users by editing
`files/jupyterhub/user_list.txt` and re-deploying the JupyterHub stack. Each line
in that file defines a user and password, separated by a colon. When JupyterHub starts,
the startup script will create those users within the JupyterHub container. The PAMAuthenticator
module authenticates against the running Docker container.

The `user_list.txt` file is mounted into the running Docker container as a
[Docker Swarm secret](https://docs.docker.com/engine/swarm/secrets/). The file shows
up in the container `/srv/jupyterhub/user_list.txt` and is configured in the
Docker Compose configuration file. If you wish to not have users created by default,
either remove the secret configuration in the Docker Compose file or remove all
content from `files/jupyterhub/user_list.txt` and re-start the JupyterHub stack.

### *THIS IS FOR DEVELOPMENT ONLY*

##### GitHub users

You can also use GitHub as an OAuth endpoint. In doing so, JupyterHub will redirect
your login to GitHub so you can authenticate there. GitHub will then redirect your
browser back to JupyterHub. JupyterHub, once verifying that you've logged into GitHub
will create a user for you and log you in as your GitHub username.

To get the GitHub OAuth working, edit your environment file (compose.env or your
  local version) and add the following row with the following content:

`AUTHENTICATOR_TYPE=github`

Now you should go to GitHub and [register your local application](https://developer.github.com/apps/building-integrations/setting-up-and-registering-oauth-apps/registering-oauth-apps/).

An example registration would look like:
- Application Name: Dockerized JupyterHub Test
- Homepage URL: https://192.168.99.101/hub
- Application Description: Dockerized JupyterHub Test Description
- Authorization callback URL: https://192.168.99.101/hub/oauth_callback

You can use the IP of any node in your swarm. Using Docker Machine, you can get the
IP by issuing `docker-machine ip <node name>`.

Once your application is registered, GitHub provides for you a client ID and a
client secret. Add the client ID your environment file. Your client ID key should be
titled `OAUTH_CLIENT_ID`. You should then add your client secret should be written
to a file. By default, the file is `files/jupyterhub/jupyterhub_oauth_github_secret`.
If, instead you'd like to use your own file, you can create one named
`files/jupyterhub/jupyterhub_oauth_github_secret_local`. This requires having the
environment variable `DOCKER_JUPYTERHUB_LOCAL_ENV` set to the value `_local` as
mentioned above in the configuration section. Otherwise, you can write your file
anywhere you like and change the `secrets.jupyterhub_oauth_secret` location in
your Docker Compose configuration file. When JupyterHub starts, it will read that
secret file and initialize JupyterHub with it.

You can also add yourself or whoever you like as administrative users in JupyterHub
by adding a list of users to the `AUTHENTICATOR_ADMIN_USERS` value in your environment
file. The list should be comma separated.

Finally, add a line to your environment file named `OAUTH_CALLBACK_URL`. This should
match the value you put into GitHub for the authorization callback URL. In this example
that would be `https://192.168.99.101/hub/oauth_callback`

An example environment file with non-real values should look like:

```
OAUTH_CALLBACK_URL=https://192.168.99.101/hub/oauth_callback
OAUTH_CLIENT_ID=dd1234567890ec
OAUTH_CLIENT_SECRET_FILE_PATH=/srv/jupyterhub/jupyterhub_oauth_github_secret
AUTHENTICATOR_ADMIN_USERS=isuftin
AUTHENTICATOR_TYPE=github
```

### Notebook Image

When a user logs into JupyterHub, JupyterHub will create a new Docker Swarm service
for that user. The service is a Docker container running a single-user Docker notebook.
This allows for the user's notebook process to be completely encapsulated within
 its own container. The image that is launched by default is the one that was created
 in the configuration above. If you want to use a different image, you can use
 any of the images [described here](https://github.com/jupyter/docker-stacks).

To change the default image used by JupyterHub, edit your environment file and update
the value for the environment `SINGLE_USER_IMAGE`. By default, the value is
`localhost:5000/dlcc/jupyter-singleuser:latest` referring to the image you built
and pushed to the local private Docker registry.

If you do change the default image, you may need to change what command runs at
startup. To do so, edit `jupyterhub_config.py` and update the array for the key
`c.SwarmSpawner.container_spec.args`.

## Launching JupyterHub

Once you have everything configured, you can launch JupyterHub by changing your working
directory to the root of this project and issuing the command `docker stack deploy jupyterhub -c docker-compose-local-registry.yml`

JupyterHub will deploy to the manager node. This is required because the Docker client
in the JupyterHub container needs to communicate with the Docker Swarm manager engine
on the host the container runs on. This is how JupyterHub is able to manage Docker
Swarm services.  The Docker Compose configuration ensures that the JupyterHub container
runs on a manager node by setting the `deploy.labels.placement.constraints` value
to `role == manager`. By default, manager nodes have this label set.

Once launched, you can view the logs for JupyterHub by issuing the `docker service logs`
command.

```
$ docker service logs jupyterhub_jupyterhub
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | Adding user testuser
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [I 2017-08-14 14:30:43.619 JupyterHub app:724] Loading cookie_secret from /srv/jupyterhub/jupyterhub_cookie_secret
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [I 2017-08-14 14:30:43.732 JupyterHub app:892] Not using whitelist. Any authenticated user will be allowed.
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [I 2017-08-14 14:30:43.824 JupyterHub swarmspawner:229] Docker service 'jupyter-5d9c68c6c50ed3d02a2fcf54f63993b6-1' is gone
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [W 2017-08-14 14:30:43.824 JupyterHub swarmspawner:194] Docker service not found
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [I 2017-08-14 14:30:43.833 JupyterHub app:1453] Hub API listening on http://0.0.0.0:8081/hub/
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [I 2017-08-14 14:30:43.837 JupyterHub app:1176] Starting proxy @ http://0.0.0.0:443/
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | 14:30:44.056 - info: [ConfigProxy] Proxying https://0.0.0.0:443 to http://127.0.0.1:8081
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | 14:30:44.060 - info: [ConfigProxy] Proxy API at http://127.0.0.1:444/api/routes
jupyterhub_jupyterhub.1.bt2f161hittp@manager    | [I 2017-08-14 14:30:44.147 JupyterHub app:1485] JupyterHub is now running at http://127.0.0.1:443/
```

If you wish to tail the logs, you can add the `-f` flag to the logs command. Hit
ctrl-c to stop tailing.

At this point you should be able to view the JupyterHub UI by accessing the JupyterHub
console using your browser. Navigate to the IP of any VM in your Docker Swarm. You can
find the IP by issuing `docker-machine ip <node name>`. It doesn't matter if JupyterHub
is not running on the node you access. The Docker Swarm mesh network will route your
call to the service.

If you've not changed the default authentication scheme, you should be able to log
in using `testuser` for a usernamr and `testpassword` for a password. If you've updated
the configuration to use GitHub as an OAuth provider, use your GitHub credentials to
do so.

You can remove your JupyterHub stack by issuing `docker stack rm jupyterhub`.

If you've logged in to JupyterHub, you may leave an orphan service running. Try
issuing `docker service ls`. If you see a service named `jupyter-<a long hash>-1`,
that service is your JupyterHub notebook and needs to be cleaned up before removing
the stack. You can issue `docker service rm <name of the service>`. After that, you
should try to remove the JupyterHub stack again.
