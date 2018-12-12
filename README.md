### Installation and Setup

Clone the repository from GitHub:
```
$ git clone https://github.com/silverjimmy/YummyRecipeApi_v.2.git
```

Fetch from the develop branch:
```
$ git fetch origin develop
```

Navigate to the `YummyRecipeApi_v.2` directory:
```
$ cd YummyRecipeApi_v.2
```

Create a virtual environment:
> Use [this guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to create and activate a virtual environment.

Install the required packages:
```
$ pip install -r requirements.txt

```

Install postgres:
```
brew install postgresql
type psql in terminal.
On postgres interactive interface, type CREATE DATABASE flask_api;
```

Create a .env file and add the following:
```
source name-of-virtual-environment/bin/activate
export FLASK_APP="run.py"
export SECRET="a-secret-key"
export DATABASE_URL="postgresql://localhost/flask_api"
```

Then run:
```
source .env
```

Run the migrations:
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

Launch the program:
```
For python3 use:
python3 run.py

Else:
python run.py
```

