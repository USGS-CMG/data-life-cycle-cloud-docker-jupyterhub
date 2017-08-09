FROM jupyterhub/jupyterhub:0.7.2

MAINTAINER Ivan Suftin <isuftin@usgs.gov>

# https://github.com/jupyterhub/oauthenticator
RUN pip install oauthenticator

# https://github.com/jupyterhub/ldapauthenticator
RUN pip install jupyterhub-ldapauthenticator

# https://github.com/yuvipanda/jupyterhub-dummy-authenticator
RUN pip install jupyterhub-dummyauthenticator

# https://github.com/jupyter/notebook
RUN pip install jupyter

# https://github.com/jupyterhub/dockerspawner
RUN git clone https://github.com/jupyterhub/dockerspawner.git /tmp/dockerspawner
RUN pip install -r /tmp/dockerspawner/requirements.txt
RUN cd /tmp/dockerspawner && pip install .
RUN rm -rf /tmp/dockerspawner

COPY files/jupyterhub/files/entrypoint.sh /srv/jupyterhub/entrypoint.sh
RUN chmod +x /srv/jupyterhub/entrypoint.sh

ENTRYPOINT ["/srv/jupyterhub/entrypoint.sh", "&&"]
