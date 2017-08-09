import os

pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')

ssl_dir = pjoin(runtime_dir, 'ssl')

# SSL Configuration
c.JupyterHub.ssl_key = pjoin(ssl_dir, 'jupyterhub_ssl_key.pem')
c.JupyterHub.ssl_cert = pjoin(ssl_dir, 'jupyterhub_ssl_cert.crt')
c.JupyterHub.port = 443

# Secret Cookie Configuration
c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/jupyterhub_cookie_secret'

# Auth Token Configuration
with open('/srv/jupyterhub/jupyterhub_proxy_auth_token', 'r') as token_file:
    c.JupyterHub.proxy_auth_token=token_file.read().rstrip('\n')

# SQLite Configuration
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')

# Logging Configuration
c.JupyterHub.extra_log_file = '/var/log/jupyterhub.log'

c.Authenticator.admin_users = { 'root' }
c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
c.DummyAuthenticator.password = 'test'

c.JupyterHub.admin_access = True
