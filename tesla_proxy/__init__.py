import sys
import time
import requests
import logging
from uuid import uuid4
from flask import Flask, Response, request, session, abort, render_template, redirect, url_for
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object('tesla_proxy.config')

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

from tesla_proxy.store import db
from tesla_proxy.oauth import password_grant, token_grant

auth = HTTPTokenAuth(scheme='Token')

@auth.verify_token
def verify_token(token):
    if check_password_hash(db.get('api_key'), token):
        return True
    return False

def generate_csrf_token():
    session['_csrf_token'] = str(uuid4())
    return session['_csrf_token']

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template("index.html", csrf_token=generate_csrf_token())

@app.route('/setup', methods=['POST'])
def setup():
    token = session.pop('_csrf_token', None)
    if not token or token != request.form.get('_csrf_token'):
        return redirect(url_for('index'))

    if request.form.get('password'):
        if check_password_hash(db.get('setup_password'), request.form.get('password')):
            session['authenticated'] = True
            return render_template("setup.html",
                    csrf_token=generate_csrf_token())
        else:
            return redirect(url_for('index'))

    success = False

    if not session.get('authenticated', False):
        return redirect(url_for('index'))

    if request.form.get('setup_password'):
        # Update setup password
        db.set('setup_password', generate_password_hash(request.form.get('setup_password')))
        success = True

    if request.form.get('api_key'):
        # Update API key
        db.set('api_key', generate_password_hash(request.form.get('api_key')))
        success = True

    if request.form.get('tesla_username') and request.form.get('tesla_password'):
        # Update tokens
        tokens = password_grant(request.form.get('tesla_username'), request.form.get('tesla_password'))
        if tokens['access_token']:
            db.set('tokens', tokens)
            success = True
        else:
            app.logger.critical("Unexpected response from token endpoint")
            app.logger.critical(tokens)

    return render_template("setup.html",
            success=success,
            csrf_token=generate_csrf_token())

@app.route('/<path:path>', methods=app.config.get('HTTP_METHODS'))
@auth.login_required
def proxy(path):
    tokens = db.get('tokens')

    if not tokens or not tokens.get('refresh_token'):
        app.logger.error("Please configure the proxy with your Tesla account")
        abort(500)

    token_expiry = tokens.get('created_at', 0) + tokens.get('expires_in', 0)
    if token_expiry < int(time.time()):
        # Access token is expired, refresh it
        tokens = token_grant(tokens.get('refresh_token'))

        if not tokens.get('access_token', None):
            app.logger.critical("Unexpected response from token endpoint")
            app.logger.critical(tokens)
            abort(500)

        db.set('tokens', tokens)

    excluded_req_headers = ['Host', 'Authorization']
    req_headers = {key: value for (key, value) in request.headers if key not in excluded_req_headers}

    req_headers['Authorization'] = f"Bearer {tokens.get('access_token', '')}"
    if 'user-agent' not in req_headers:
        req_headers['User-Agent'] = app.config.get('USER_AGENT')

    # Proxy the request
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, f"{app.config.get('API_BASE')}/"),
        headers=req_headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_resp_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    resp_headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_resp_headers]

    response = Response(resp.content, resp.status_code, resp_headers)
    return response
