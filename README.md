# Description
A simple match history API for the Lambda Wars game (http://lambdawars.com), written using Flask.
Provides rest api to record or retrieves matches and validates the players against the Steam api.

# Requirements

- Python
- Virtualenv: pip install virtualenv

# Setup

1. virtualenv venv
2. venv/bin/activate
3. pip install -r requirements.txt

# Run development server

1. venv/bin/activate
2. python run.py

# MySQL database

By default it creates a sqlite database. To connect to a mysql database, do:

1. Install the MySQLdb module: pip install MySQL-python
2. Open instance/application.cfg (create if needed)
3. Add the following configuration line and adjust for your database:
```SQLALCHEMY_DATABASE_URI = 'mysql://username:password@server/database'```