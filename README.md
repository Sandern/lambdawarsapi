Requirements:
- Python
- Virtualenv: pip install virtualenv

Setup (install + database):
1. virtualenv venv
2. venv/bin/activate
3. pip install -r requirements.txt
4. python
5. from app.database import db
6. db.create_all()

Run dev server:
1. venv/bin/activate
2. python run.py

