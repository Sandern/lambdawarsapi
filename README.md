# Requirements

- Python
- Virtualenv: pip install virtualenv

# Setup (install + database)

1. virtualenv venv
2. venv/bin/activate
3. pip install -r requirements.txt

# Run development server

1. venv/bin/activate
2. python run.py

# MySQL database

By default it creates a sqlite database. To connect to a mysql database, do:

1. Install the MySQLdb module: pip install python-mysql
2. Open instance/application.cfg (create if needed)
3. Add the following configuration line and adjust for your database:
```SQLALCHEMY_DATABASE_URI = 'mysql://username:password@server/database'```