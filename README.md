# Description
A simple match history API for the Lambda Wars game (https://lambdawars.com), written using Flask.
Provides rest api to record or retrieves matches and validates the players against the Steam api.

# Requirements

- Python
- Virtualenv: pip install virtualenv

# Setup

1. virtualenv venv
1. venv/bin/activate
1. pip install -r requirements.txt

# Run development server

1. venv/bin/activate
1. python run.py

# MySQL database

By default it creates a sqlite database. To connect to a mysql database, do:

1. Open instance/application.cfg (create if needed)
1. Add the following configuration line and adjust for your database:
```SQLALCHEMY_DATABASE_URI = 'mysql://username:password@server/database'```