import os

c = get_config()

pjoin = os.path.join

runtime_dir = os.path.join('/srv/jupyterhub')
ssl_dir = pjoin(runtime_dir, 'ssl')

# SSL Configuration
c.JupyterHub.ssl_key = os.getenv('SSL_KEY', pjoin(ssl_dir, os.getenv('SSL_FILE_KEY', 'jupyterhub_ssl_key.pem')))
c.JupyterHub.ssl_cert = os.getenv('SSL_CERT', pjoin(ssl_dir, os.getenv('SSL_FILE_CERT', 'jupyterhub_ssl_cert.crt')))
c.JupyterHub.port = int(os.getenv('SSL_PORT', 443))

# Secret Cookie Configuration
c.JupyterHub.cookie_secret_file = os.getenv('COOKIE_FILE', pjoin(runtime_dir, 'jupyterhub_cookie_secret'))

# Auth Token Configuration
token_file_path = os.getenv('TOKEN_FILE_PATH', pjoin(runtime_dir, 'jupyterhub_proxy_auth_token'))
with open(token_file_path, 'r') as token_file:
    c.JupyterHub.proxy_auth_token = token_file.read().rstrip('\n')

# SQLite Configuration
c.JupyterHub.db_url = os.getenv('DB_URL', pjoin(runtime_dir, 'jupyterhub.sqlite'))

# Logging Configuration
c.JupyterHub.extra_log_file =  os.getenv('EXTRA_LOG_FILE', '/var/log/jupyterhub.log')

c.JupyterHub.ip = os.getenv('JUPYTERHUB_IP', '0.0.0.0')
c.JupyterHub.hub_ip = os.getenv('JUPYTERHUB_HUB_IP', '0.0.0.0')
c.JupyterHub.hub_port = int(os.getenv('JUPYTERHUB_HUB_PORT', 8081))

# Authenticator configuration
c.JupyterHub.admin_access = True
c.Authenticator.admin_users = set(os.getenv('AUTHENTICATOR_ADMIN_USERS', '').split(","))
if os.getenv('AUTHENTICATOR_TYPE') == 'github':
    from oauthenticator.github import GitHubOAuthenticator
    c.JupyterHub.authenticator_class = GitHubOAuthenticator

    c.GitHubOAuthenticator.oauth_callback_url = os.getenv('OAUTH_CALLBACK_URL', 'https://localhost/hub/oauth_callback')
    c.GitHubOAuthenticator.client_id = os.getenv('OAUTH_CLIENT_ID', '')
    c.GitHubOAuthenticator.client_secret = os.getenv('OAUTH_CLIENT_SECRET', '')
    oauth_client_secret_file_path = os.getenv('OAUTH_CLIENT_SECRET_FILE_PATH', '')
    if c.GitHubOAuthenticator.client_secret == '' and oauth_client_secret_file_path != '':
        with open(oauth_client_secret_file_path, 'r') as secret_file:
            c.GitHubOAuthenticator.client_secret = secret_file.read().rstrip('\n')

# Spawner Configuration
if os.getenv('JUPYTERHUB_SPAWNER', '') == 'swarmspawner':
    c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'
    c.SwarmSpawner.jupyterhub_service_name = os.getenv('SWARMSPAWNER_JUPYTERHUB_SERVICE_NAME', 'jupyterhub_jupyterhub')
    c.SwarmSpawner.networks = [os.getenv('SWARMSPAWNER_JUPYTERHUB_NETWORKS', 'jupyterhub_dlcc_network')]
    c.SwarmSpawner.start_timeout = 60 * 5
    notebook_dir = os.getenv('NOTEBOOK_DIR', '/home/jovyan/work')
    c.SwarmSpawner.notebook_dir = notebook_dir
    mounts = [{
        'type': 'volume',
        'source': 'jupyterhub-user-{username}',
        'target': notebook_dir
    }]
    c.SwarmSpawner.container_spec = {
        'args': ['/usr/local/bin/start-singleuser.sh'],
        'Image': os.getenv('SINGLE_USER_IMAGE', 'jupyterhub/singleuser:latest'),
        'mounts': mounts
    }
    c.SwarmSpawner.use_user_options = True
    user_options = {
        'placement' : ["node.Role == worker"]
    }
