import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime, timezone
import plotly.express as px

from helpers import login_required, lookup

# Configure flask
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Connect db to SQLite database
conn = sqlite3.connect("portfolio.db", check_same_thread=False)
conn.row_factory = (
    sqlite3.Row
)  # Allows refering to columns by dict values rather than array index
cur = conn.cursor()

# Create new table - users(id,username,hash), username must be unique
cur.execute(
    " CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL)"
)
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users(username)")

# Create new table - orders(id,user_id,symbol,shares,price,timestamp)
cur.execute(
    "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, symbol TEXT NOT NULL, shares INTEGER NOT NULL, price NUMERIC NOT NULL, timestamp TEXT NOT NULL)"
)
cur.execute("CREATE INDEX IF NOT EXISTS order_by_user_id ON orders(user_id)")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for valid registeration
        if not (username and password and confirmation):
            flash("Please fill in all rows")
            return render_template("register.html")
        if (
            cur.execute("SELECT * FROM users WHERE username=?", [username]).fetchone()
            is not None
        ):
            flash("Username is taken!")
            return render_template("register.html")
        if password != confirmation:
            flash("Passwords do not match")
            return render_template("register.html")

        # Insert new user into database
        cur.execute(
            "INSERT INTO users(username,hash) VALUES(?,?)",
            [username, generate_password_hash(password)],
        )
        conn.commit()

        # Log the user in
        user_info = cur.execute(
            "SELECT id FROM users WHERE username=?", [username]
        ).fetchone()
        session["user_id"] = user_info["id"]
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_info = cur.execute(
            "SELECT * FROM users WHERE username=?", [username]
        ).fetchone()

        # Ensure user entered the form
        if not username:
            flash("Please enter a username")
            return render_template("login.html")
        if not password:
            flash("Please enter a password")
            return render_template("login.html")

        # Ensure credentials entered are correct
        if username != user_info["username"] or not check_password_hash(
            user_info["hash"], password
        ):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Logs user in if credentials were right
        session["user_id"] = user_info["id"]

        # Redirects user to homepage
        return redirect("/")


@app.route("/logout", methods=["GET"])
def logout():
    if request.method == "GET":
        session.clear()
        return redirect("/")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "GET":
        return render_template("add.html")

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        price = float(request.form.get("price"))
        date = request.form.get("date")

        user_id = session["user_id"]

        result = lookup(symbol)
        print(result)

        # Ensure that symbol exists
        if not result:
            flash("Symbol does not exist")
            return render_template("add.html")

        # Insert purchase detail into orders table
        cur.execute(
            "INSERT INTO orders(user_id,symbol,shares,price,timestamp) VALUES(?,?,?,?,?)",
            [user_id, symbol, shares, price, date],
        )
        conn.commit()

        return render_template("add.html")


@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    if request.method == "GET":
        return render_template("portfolio.html")

    # if request.method=="POST":
    # Graphing function
