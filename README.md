# Alchemy Server

## Initialization
- Running the command to download the repo: `git clone https://github.com/leebird/alchemy-server`
- Init the submodules: `git submodule init`
- Create a Python 3 virtual enviroment: `virtualenv --python=python3 env`
- Acticate Python virtual environment: `. env/bin/activate`
- Install Python modules: `pip install -r requirements.txt`

## Create Database
- Create a MySQL database
- Import the database dump (the one on lysine)
- Modify alchemy_server/settings.py to match the created database
- Start the development server by running `python manage.py runserver`

## Django
- Admin interface: http://yoursite/admin with account test/test.
- Brat visualization: http://yoursite/brat/PMID. (replace 'PMID' with a real PMID)

## Note
The project is based on Django (https://www.djangoproject.com/). I suggest reading the Django tutorials (https://docs.djangoproject.com/en/1.9/intro/tutorial01/) if there are problems.

