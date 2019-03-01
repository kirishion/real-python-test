import sqlite3
from _config import DATABASE_PATH
from views import db
from models import Task
from datetime import date

db.create_all()

#db.session.add(Task("Finish this tutorial", date(2016, 9, 22), 10, 1))
#db.session.add(Task("Finish Real Python", date(2016, 10, 3), 10, 1))


db.session.commit()



