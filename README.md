Juntagrico Heroku Template for cookiecutter
===========

This template sets up a project to be used with heroku as hosting.

# Setting up locally to test setup

On any environment install Python 3, and add it to your path

## UNIX

### Set your environment variables

This should do it for your local setup:

``` bash
    export JUNTAGRICO_AWS_KEY_ID=
    export JUNTAGRICO_AWS_KEY=
    export JUNTAGRICO_AWS_BUCKET_NAME=
```

### Installing requirements

    sudo easy_install pip
    sudo pip install virtualenv
    virtualenv --distribute venv
    source ./venv/bin/activate
    pip install --upgrade -r requirements.txt

### Setup DB

    ./manage.py migrate
    
### Setup Admin User

    ./manage.py createsuperuser
    ./manage.py create_member_for_superusers
    
### Create Tesdata (not required)

Simple

    ./manage.py generate_testdata

More complex

    ./manage.py generate_testdata_advanced
    
### Run the server

    ./manage.py runserver

## Windows

### Set your environment variables

This should do it for your local setup:

``` bash
    set JUNTAGRICO_AWS_KEY_ID=
    set JUNTAGRICO_AWS_KEY=
    set JUNTAGRICO_AWS_BUCKET_NAME=
```

### Installing requirements

    pip install virtualenv
    virtualenv --distribute venv
    venv\Scripts\activate.bat
    pip install --upgrade -r requirements.txt

### Setup DB

    python -m manage migrate
    
### Setup Admin User

    python -m manage createsuperuser
    python -m manage create_member_for_superusers
    
### Create Tesdata (not required)

Simple

    python -m manage generate_testdata

More complex

    python -m manage generate_testdata_advanced
    
### Run the server

    python -m manage runserver
    
#Heroku

you have to login to a heroku bash and setup the db and create the admin user as desbribed in the UNIX section
    
    




