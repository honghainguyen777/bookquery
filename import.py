import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import csv

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, hash VARCHAR NOT NULL)")
print("Table users is created")
db.execute("CREATE TABLE books(title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL, isbn VARCHAR UNIQUE NOT NULL, ratings_count INTEGER NOT NULL, review_count INTEGER NOT NULL, average_rating NUMERIC NOT NULL)")
print("Table books is created")
db.execute("CREATE TABLE reviews(username VARCHAR NOT NULL, book_isbn VARCHAR NOT NULL, rating INTEGER NOT NULL, review VARCHAR, recorded date NOT NULL DEFAULT CURRENT_DATE)")
print("Table reviews is created")
db.execute("CREATE TABLE QAs(qa_id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, book_isbn VARCHAR NOT NULL, qa_question VARCHAR NOT NULL, recorded date NOT NULL DEFAULT CURRENT_DATE)")
print("Table QAs is created")
db.execute("CREATE TABLE responses(username VARCHAR NOT NULL, book_isbn VARCHAR NOT NULL, qa_id INTEGER NOT NULL, response VARCHAR NOT NULL, recorded date NOT NULL DEFAULT CURRENT_DATE)")
print("Table responses is created")
# make something where user can ask about the book and get answer from other
db.execute("CREATE TABLE stores(book_isbn VARCHAR NOT NULL, store_name VARCHAR NOT NULL, store_link VARCHAR NOT NULL)")
print("Table stores is created")

f = open("books.csv")
reader = csv.reader(f)

for isbn, title, author, year in reader:
    if isbn != "isbn":
        print(isbn)
        db.execute("INSERT INTO books (title, author, year, isbn, ratings_count, review_count, average_rating) VALUES (:title, :author, :year, :isbn, 0, 0, 0)",
                   {"title": title, "author": author, "year": year, "isbn": isbn})
print("data is imported")
print("All tables created")
db.commit()
