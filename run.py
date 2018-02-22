import os
import sys
from app import create_app

config_name = os.getenv('ENV')
app = create_app("production")
response.headers.add('Access-Control-Allow-Origin', '*')
response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
if __name__ == '__main__':
    app.run()
