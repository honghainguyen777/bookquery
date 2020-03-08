import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import csv

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("DROP TABLE responses")
db.execute("DROP TABLE qas")
db.execute("DROP TABLE reviews")
db.execute("DROP TABLE users")
db.execute("DROP TABLE books")
db.execute("DROP TABLE stores")
print("dropped")
db.commit()
