import requests
from tesla_proxy import config

def password_grant(email, password):
    return requests.post(f'{config.API_BASE}/oauth/token?grant_type=password',
            headers={
                'user-agent': config.USER_AGENT
            },
            data={
                'grant_type': 'password',
                'client_id': config.OAUTH_CLIENT_ID,
                'client_secret': config.OAUTH_CLIENT_SECRET,
                'email': email,
                'password': password
            }).json()

def token_grant(refresh_token):
    return requests.post(f'{config.API_BASE}/oauth/token?grant_type=refresh_token',
            headers={
                'user-agent': config.USER_AGENT
            },
            data={
                'grant_type': 'refresh_token',
                'client_id': config.OAUTH_CLIENT_ID,
                'client_secret': config.OAUTH_CLIENT_SECRET,
                'refresh_token': refresh_token
            }).json()

