Juntagrico Template for cookiecutter
===========

This template sets up a project.

# Setting up locally to test setup

On any environment install Python 3, and add it to your path

## UNIX

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





