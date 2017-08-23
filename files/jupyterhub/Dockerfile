FROM jupyterhub/jupyterhub:0.7.2

MAINTAINER Ivan Suftin <isuftin@usgs.gov>

RUN pip install --no-cache-dir --upgrade pip

# https://github.com/jupyterhub/oauthenticator
RUN pip install --no-cache-dir oauthenticator

# https://github.com/jupyter/notebook
RUN pip install --no-cache-dir jupyter

# https://github.com/docker/docker-py
RUN pip install --no-cache-dir docker

# Install Docker on the running container
RUN wget https://get.docker.com -q -O /tmp/getdocker && \
    chmod +x /tmp/getdocker && \
    sh /tmp/getdocker && \
    rm /tmp/getdocker && \
    apt-get -y clean && apt-get -y autoremove

# Install the Docker Swarm spawner
RUN git clone https://github.com/isuftin/SwarmSpawner /tmp/SwarmSpawner && \
  cd /tmp/SwarmSpawner && python setup.py install && \
  rm -rf /tmp/SwarmSpawner

COPY entrypoint.sh /srv/jupyterhub/entrypoint.sh
RUN chmod +x /srv/jupyterhub/entrypoint.sh

ENTRYPOINT ["/srv/jupyterhub/entrypoint.sh", "&&"]
