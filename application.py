import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from helpers import login_required
import string

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    """index"""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
@login_required
def search():
    """Search for a book"""

    # Make sure if the user typed correctly
    if not request.form.get("search"):
        flash("You must provide isbn, title, or author in the search field")
        return render_template("index.html")

    # get user typed string
    search_text = request.form.get("search")

    # capitalize all words and add will card to the string
    in_text = "%" + string.capwords(search_text) + "%"

    # search the text in the database
    data = db.execute(
        "SELECT * FROM books WHERE (title LIKE :in_text OR author LIKE :in_text OR isbn LIKE :in_text) ORDER BY ratings_count DESC", {"in_text": in_text}).fetchall()

    # check if the query return something
    if len(data) == 0:
        # if not, render the search.html for another search engine
        flash("NOT FOUND IN OUR DATABASE")
        return render_template("search.html", search_text=search_text)
    else:
        # else, render the search results
        return render_template("search_result.html", data=data, search_text=search_text)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register for an account"""

    # check if the request is POST
    if request.method == "POST":

        # get typed username from user
        username = request.form.get("username").lower()

        # get typed password from user
        password = request.form.get("password")

        # get the repeated password
        confirmation = request.form.get("confirmation")

        # check if the password and repeated one are matched
        if password != confirmation:
            # passwords do not match
            flash("Passwords do not match")
            # reload the register page
            return render_template("register.html")

        # check if the username exists in the user database
        elif db.execute("SELECT username FROM users WHERE username=:username", {"username": username}).fetchone():
            # if yes, then flash an alert and reload the page
            flash("Username has already existed!")
            return render_template("register.html")

        # username is acceptted
        else:
            # generate a hash for password protection
            hashed_password = generate_password_hash(password)

            # insert it to users table
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                       {"username": username, "hash": hashed_password})

            # log the user in and remember the user's id in the session
            session["user_id"] = (db.execute(
                "SELECT id FROM users WHERE username = :username", {"username": username}).fetchone())[0]

            # commit changes in the database
            db.commit()
            flash("Registered!")
            # redirect to the search page
            return redirect("/")

    # if guest clicks to register page
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login request"""

    # first, clear all the existing data in session
    session.clear()

    # if the request is POST
    if request.method == "POST":

        # get typed username and password from user
        username = request.form.get("username").lower()
        password = request.form.get("password")

        # query all information about the username in the users table
        user_data = db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        # if the username does not match or the typed password is not correct
        if user_data == None or not check_password_hash(user_data["hash"], password):
            # alert a fail and reload the page
            flash("Invalid username/password!")
            return render_template("login.html")

        # if the typed data are correct, login and remember the user_id
        session["user_id"] = user_data[0]

        # redirect to search page
        return redirect("/")

    # if user wants to login
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout"""

    # clear all saved data
    session.clear()
    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Changing password"""

    # if the request is POST
    if request.method == "POST":

        # get current user_id in the session
        user_id = session["user_id"]

        # get user inputs (username, password and its confirmation)
        current_password = request.form.get("password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # check if the typed passwords are the same
        if new_password != confirmation:
            flash("Password does not match")
            return render_template("account.html")

        # query for user information
        user = db.execute("SELECT hash FROM users WHERE id = :user_id", {
                          "user_id": user_id}).fetchone()

        # check if the current password hash matches the database
        if not check_password_hash(user[0], current_password):
            flash("Wrong current password!")
            return render_template("/account.html")
        else:
            # hash the new password and update the database
            hash = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", {
                       "hash": hash, "user_id": user_id})

            # flash a success, commit the change in db and log the user out
            flash("Password has been changed!")
            db.commit()
            return redirect("/logout")

    # if user wants to change her/his password
    else:
        return render_template("account.html")


@app.route("/google_search", methods=["POST"])
@login_required
def google_search():
    """Google search engine"""

    # get the typed-in and redirect to google engine if the user clicks
    search_text = request.form.get("search")
    return redirect("http://www.google.com/search?q=" + search_text)


@app.route("/gr_search", methods=["POST"])
@login_required
def gr_search():
    """Goodreads search engine"""

    # get the typed-in and redirect to Goodreads engine if the user clicks
    search_text = request.form.get("search")
    return redirect("http://www.goodreads.com/search?q=" + search_text)


@app.route("/book/<isbn>", methods=["GET"])
@login_required
def book(isbn):
    """Render a book page"""

    # get current user_id in the session
    user_id = session["user_id"]

    # get the username associated to the user_id from db
    username = db.execute("SELECT username FROM users WHERE id = :user_id", {
                          "user_id": user_id}).fetchone()[0]

    # take the book info corresponding to its isbn from db
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                      {"isbn": isbn}).fetchone()

    # take all reviews that were added for this book from reviews table
    reviews = db.execute(
        "SELECT * FROM reviews WHERE book_isbn=:isbn AND review IS NOT NULL ORDER BY recorded", {"isbn": isbn}).fetchall()

    # take all QAs that were added for this book from QAs table
    QAs = db.execute(
        "SELECT * FROM QAs WHERE book_isbn=:isbn ORDER BY recorded", {"isbn": isbn}).fetchall()

    # take all answers for every QAs that were added for this book from responses table
    responses = db.execute(
        "SELECT * FROM responses WHERE book_isbn=:isbn ORDER BY recorded", {"isbn": isbn}).fetchall()

    # current user's review
    user_review = db.execute(
        "SELECT review FROM reviews WHERE book_isbn=:isbn AND username = :username", {"isbn": isbn, "username": username}).fetchone()

    # current user's rating
    user_rating = db.execute(
        "SELECT rating FROM reviews WHERE book_isbn=:isbn AND username = :username", {"isbn": isbn, "username": username}).fetchone()

    # query for goodreads book's data
    res_rc = requests.get("https://www.goodreads.com/book/review_counts.json",
                          params={"key": "0jGT6iWdVS4bgemTPVSjBg", "isbns": isbn})

    # Take only the necessary information
    book_rc = res_rc.json()["books"][0]

    """JSON will be like:
    {"id":50019613,"isbn":"0441172717","isbn13":"9780441172719","ratings_count":241,
    "reviews_count":614,"text_reviews_count":13,"work_ratings_count":674280,"work_reviews_count":1163860,
    "work_text_reviews_count":18697,"average_rating":"4.22"}
    call book_rc["reviews_count"] or book_rc["average_rating"] or book_rc["work_ratings_count"] for reviews_count, average_rating, or ratings_count
    """

    # return all data into a book.html template
    return render_template("book.html", book=book, book_rc=book_rc, reviews=reviews, QAs=QAs, responses=responses, user_rating=user_rating, user_review=user_review)


@app.route("/rating", methods=["POST"])
@login_required
def rating():
    """Rate a book"""

    # get current user_id in the session
    user_id = session["user_id"]

    # get the username associated to the user_id from db
    username = db.execute(
        "SELECT username FROM users WHERE id = :user_id", {"user_id": user_id}).fetchone()[0]

    # get the current book's isbn
    isbn = request.form.get("isbn")

    # get rating from user
    user_rating = request.form.get("rating")

    # insert the rating to the book
    db.execute("INSERT INTO reviews (username, book_isbn, rating) VALUES(:username, :isbn, :user_rating)",
               {"username": username, "isbn": isbn, "user_rating": user_rating})

    # query for the rating count of the book and update it with the new value
    ratings_count = db.execute(
        "SELECT ratings_count FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()[0] + 1
    db.execute("UPDATE books SET ratings_count=:ratings_count WHERE isbn=:isbn",
               {"ratings_count": ratings_count, "isbn": isbn})

    # query for the average rating and update it with the new value
    avg_rating = round(db.execute("SELECT SUM(rating) AS total FROM reviews WHERE book_isbn=:isbn", {
                       "isbn": isbn}).fetchone()[0] / ratings_count, 2)
    db.execute("UPDATE books SET average_rating=:average_rating WHERE isbn=:isbn",
               {"average_rating": avg_rating, "isbn": isbn})

    # commit all changes and redirect to the book/isbn
    db.commit()
    flash("Thank you for your rating!")
    return redirect("/book/" + isbn)


@app.route("/review", methods=["POST"])
@login_required
def review():
    """Review a book"""

    # get current user_id in the session
    user_id = session["user_id"]

    # get the username associated to the user_id from db
    username = db.execute(
        "SELECT username FROM users WHERE id = :user_id", {"user_id": user_id}).fetchone()[0]

    # get the current book's isbn
    isbn = request.form.get("isbn")

    # check if the POST request is for rating
    if request.form.get("rating"):
        # if yes, then insert the rating into reviews table
        db.execute("INSERT INTO reviews (username, book_isbn, rating) VALUES(:username, :isbn, :rating)",
                   {"username": username, "isbn": isbn, "rating": request.form.get("rating")})

        # query for the rating count of the book and update it with the new value
        ratings_count = db.execute("SELECT ratings_count FROM books WHERE isbn=:isbn", {
                                   "isbn": isbn}).fetchone()[0] + 1
        db.execute("UPDATE books SET ratings_count=:ratings_count WHERE isbn=:isbn",
                   {"ratings_count": ratings_count, "isbn": isbn})

        # query for the average rating and update it with the new value
        avg_rating = round(db.execute("SELECT SUM(rating) AS total FROM reviews WHERE book_isbn=:isbn", {
                           "isbn": isbn}).fetchone()[0] / ratings_count, 2)
        db.execute("UPDATE books SET average_rating=:average_rating WHERE isbn=:isbn",
                   {"average_rating": avg_rating, "isbn": isbn})

    # check if the POST request is for review
    if request.form.get("review"):
        # if yes, then update the review into reviews table (rating is needed)
        review = request.form.get("review")
        db.execute("UPDATE reviews SET review=:review WHERE username=:username AND book_isbn=:isbn", {
                   "review": review, "username": username, "isbn": isbn})

        # query for the review count and update it with the new value
        review_count = db.execute(
            "SELECT review_count FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()[0] + 1
        db.execute("UPDATE books SET review_count=:review_count WHERE isbn=:isbn",
                   {"review_count": review_count, "isbn": isbn})

    # commit all changes and redirect to the book/isbn
    db.commit()
    flash("Thank you for your review!")
    return redirect("/book/" + isbn)


@app.route("/qa", methods=["POST"])
@login_required
def qa():
    """Add question or answer"""

    # get current user_id in the session
    user_id = session["user_id"]

    # get the username associated to the user_id from db
    username = db.execute(
        "SELECT username FROM users WHERE id = :user_id", {"user_id": user_id}).fetchone()[0]

    # get the current book's isbn
    isbn = request.form.get("isbn")

    # check if user is POST a question
    if request.form.get("qa_question"):
        # if yes, then insert it to the QAs table
        db.execute("INSERT INTO QAs (username, book_isbn, qa_question) VALUES (:username, :book_isbn, :qa_question)",
                   {"username": username, "book_isbn": isbn, "qa_question": request.form.get("qa_question")})
        flash("Thank you for your question!")

    # check if user is POST an answer
    if request.form.get("response"):
        # if yes, then get the qa id and insert the answer to the responses table
        qa_id = request.form.get("qa_id")
        db.execute("INSERT INTO responses (username, book_isbn, qa_id, response) VALUES (:username, :book_isbn, :qa_id, :response)",
                   {"username": username, "book_isbn": isbn, "qa_id": qa_id, "response": request.form.get("response")})
        flash("Thank you for your answer!")

    # commit all changes and redirect to the book/isbn
    db.commit()
    return redirect("/book/" + isbn)


@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api(isbn):
    """Request for an API pull"""

    # query all data corresponding to the book ISBN
    data = db.execute("SELECT * FROM books WHERE isbn=:isbn",
                      {"isbn": isbn}).fetchone()

    # if empty data, the return a json error coded 404
    if data == None:
        return jsonify("You entered an invalid book ISBN"), 404

    # else, change the data to dictionary format
    json_data = dict(data.items())

    # change the average_rating to float format
    json_data["average_rating"] = float(json_data["average_rating"])

    # return the json data
    return jsonify(json_data)
