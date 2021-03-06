#Viraj Dissanayake
#CS50 Project1
import os
import requests
import json

from flask import Flask, session,render_template,request,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

#index
@app.route("/")
def index():
    try:
        return render_template("index.html", user=session["user_username"])
    except KeyError:
        return render_template("index.html")
#register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if db.execute("SELECT * FROM users WHERE username = :name", {"name": name}).rowcount == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:name, :password)", {"name": name, "password": password})
            db.commit()

            return render_template("register.html", message='You have successfully registered!')
        else:
            return render_template("register.html", error='This Username already exists!')
    else:
        return render_template("register.html")
#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if (name or password) == '':
            return render_template("login.html", error="Please enter username and password")
        else:
            user = db.execute("SELECT * FROM users WHERE username = :name AND password = :password", {"name": name, "password": password}).fetchone()
            if user == None:
                return "Invalid username!"
            else
                session["user_id"] = user.id
                session["user_username"] = user.username
            return redirect(url_for("index"))
    return render_template("login.html")
#search
@app.route("/search", methods=["GET", "POST"])
def search():
    try:
        user = session["user_username"]
        if request.method == "POST":
            query = request.form.get("query")
            query_extend = '%' + query + '%'

            suggestions = db.execute("SELECT * FROM books JOIN author ON author.id = books.author_id JOIN year ON year.id = books.year_id WHERE\
             isbn LIKE :query OR title LIKE :query OR name LIKE :query LIMIT 5",
            {"query": query_extend}).fetchall()

            if suggestions == []:
                suggestions = None
            return render_template("search.html", suggestions=suggestions, query=query, user=session["user_username"])
        else:
            nothing = True
            return render_template("search.html", nothing=nothing, user=session["user_username"])
    except KeyError:
        return redirect(url_for("index"))
#review
@app.route("/book/<string:isbn_code>", methods=["GET", "POST"])
def book(isbn_code):
    try:
        user = session["user_username"]
        msg = None
        if request.method == "POST":
            comment = request.form.get("comment")
            rating = int(request.form.get("rating"))
            if comment is not '':
                if db.execute("SELECT comments.id, books.title FROM comments JOIN books ON books.id = comments.book_id WHERE user_id = :user_id AND isbn = :isbn", {"user_id": session["user_id"], "isbn": isbn_code}).rowcount == 0:
                    book_id = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn_code}).fetchone()
                    db.execute("INSERT INTO comments (comment, rating, user_id, book_id) VALUES (:comment, :rating, :user_id, :book_id)", {"comment": comment, "rating": rating, "user_id": session["user_id"], "book_id": book_id.id})
                    db.commit()
                else:
                    msg = 'Your prvious comment has been saved!'
        book = db.execute("SELECT * FROM books JOIN author ON author.id = books.author_id JOIN year ON year.id = books.year_id WHERE isbn = :isbn",
                  {"isbn": isbn_code}).fetchone()
        comments = db.execute("SELECT comment, date::date, username FROM comments JOIN users ON users.id = comments.user_id JOIN books ON books.id = comments.book_id WHERE isbn = :isbn_code", {"isbn_code": isbn_code}).fetchall()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "uXbOXIgl6R0fJSQz0nHbwg", "isbns": isbn_code})
        average = res.json()
        return render_template("book.html", book=book, comments=comments, notice=notice, average=average["books"][0])
    except KeyError:
        return redirect(url_for("index"))
#API Access
@app.route("/api/<string:isbn_code>")
def api(isbn_code):
    data = db.execute("SELECT * FROM books JOIN author ON author.id = books.author_id JOIN year ON year.id = books.year_id WHERE isbn = :isbn", {"isbn":isbn_code}).fetchone()
    if data == None:
        return 'Invalid isbn!', 404
    else:
        return json.dumps(dict(data))
#logout
@app.route("/logout")
def logout():
    try:
        del session["user_id"]
        del session["user_username"]
        return redirect(url_for("index"))
    except KeyError:
        return redirect(url_for("index"))
