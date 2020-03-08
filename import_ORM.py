from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv


db.SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)


class Book(db.Model):
    __tablename__ = "books"
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String, primary_key=True, nullable=False)
    review_count = db.Column(db.Integer)
    average_score = db.Column(db.Float)


class Review(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_isbn = db.Column(db.String, db.ForeignKey(
        "books.isbn"), nullable=False)
    rates = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())
# check if the review is empty if empty then user can add review later
# add number of review not no.of ratings


class QandA(db.Model):
    __tablename__ = "QAs"
    qa_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_isbn = db.Column(db.String, db.ForeignKey(
        "books.isbn"), nullable=False)
    qa_question = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())


class Response_QA(db.Model):
    __tablename__ = "responses"
    response_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_isbn = db.Column(db.String, db.ForeignKey(
        "books.isbn"), nullable=False)
    qa_id = db.Column(db.String, db.ForeignKey("QAs.qa_id"), nullable=False)
    response = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
# make something where user can ask about the book and get answer from other


class Store(db.Model):
    __tablename__ = "stores"
    store_id = db.Column(db.Integer, primary_key=True)
    book_isbn = db.Column(db.String, db.ForeignKey(
        "books.isbn"), nullable=False)
    store_name = db.Column(db.String, nullable=False)
    store_link = db.Column(db.String, nullable=False)


f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    book = Book(title=title, author=author, year=year, isbn=isbn)
    db.session.add(book)
db.session.commit()
