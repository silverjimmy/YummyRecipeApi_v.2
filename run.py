import os
import sys
from app import create_app

config_name = os.getenv('ENV')
app = create_app("development")
request.headers['Access-Control-Allow-Origin'] = '*'

if __name__ == '__main__':
    app.run()
