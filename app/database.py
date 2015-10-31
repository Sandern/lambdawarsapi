from flask.ext.sqlalchemy import SQLAlchemy

from . import app

db = SQLAlchemy(app)

import app.models

# Make sure database is created after importing the models
db.create_all()
db.session.commit()
