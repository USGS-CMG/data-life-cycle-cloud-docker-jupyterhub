FROM jupyterhub/jupyterhub:0.7.2

MAINTAINER Ivan Suftin <isuftin@usgs.gov>

RUN pip install --upgrade pip

# https://github.com/jupyterhub/oauthenticator
RUN pip install oauthenticator

# https://github.com/jupyter/notebook
RUN pip install jupyter

# https://github.com/docker/docker-py
RUN pip install docker

# Install Docker on the running container
RUN wget https://get.docker.com -q -O /tmp/getdocker && \
    chmod +x /tmp/getdocker && \
    sh /tmp/getdocker

# Install the Docker Swarm spawner
ENV VERSION_SWARM_SPAWNER="v0.10.0"
RUN git clone https://github.com/cassinyio/SwarmSpawner /tmp/SwarmSpawner
RUN cd /tmp/SwarmSpawner && git checkout $VERSION_SWARM_SPAWNER && python setup.py install
RUN rm -rf /tmp/SwarmSpawner

COPY entrypoint.sh /srv/jupyterhub/entrypoint.sh
RUN chmod +x /srv/jupyterhub/entrypoint.sh

ENTRYPOINT ["/srv/jupyterhub/entrypoint.sh", "&&"]
