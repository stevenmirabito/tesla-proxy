import sys
import pickle
import secrets
from os import path
from werkzeug.security import generate_password_hash
from tesla_proxy import app
from tesla_proxy.config import DB_PATH

class Store:
    def __init__(self):
        if path.exists(DB_PATH):
            with open(DB_PATH, 'rb') as db_file:
                self.db = pickle.load(db_file)
        else:
            setup_password = secrets.token_hex(16)
            app.logger.warn(f'Initializing database, setup password: {setup_password}')

            self.db = {
                'setup_password': generate_password_hash(setup_password),
                'api_key': generate_password_hash(secrets.token_hex(16))
            }

            self.save()

    def save(self):
        with open(DB_PATH, 'wb') as db_file:
            pickle.dump(self.db, db_file)

    def set(self, key, value):
        self.db[key] = value
        self.save()

    def get(self, key, default=None):
        return self.db.get(key, default)

db = Store()
