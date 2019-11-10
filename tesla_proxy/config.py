import re
import secrets
from os import environ as env

SECRET_KEY = env.get('TESLA_PROXY_SECRET_KEY', secrets.token_hex(16))
USER_AGENT = env.get('TESLA_PROXY_USER_AGENT', 'tesla-proxy')
API_BASE = env.get('TESLA_PROXY_API_BASE', 'https://owner-api.teslamotors.com')
DB_PATH = env.get('TESLA_PROXY_DB_PATH', 'data.db')

OAUTH_CLIENT_ID = env.get('TESLA_PROXY_OAUTH_CLIENT_ID', '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384')
OAUTH_CLIENT_SECRET = env.get('TESLA_PROXY_OAUTH_CLIENT_SECRET', 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3')

HTTP_METHODS = env.get('TESLA_PROXY_HTTP_METHODS', 'GET,HEAD,POST,PUT,DELETE,CONNECT,OPTIONS,TRACE,PATCH')
HTTP_METHODS = re.sub(r'\s+', '', HTTP_METHODS).split(',')
