import os
import sys
from app import create_app

config_name = os.getenv('ENV')
app = create_app("production")

@blueprint.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run()
