import os

# from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)

# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finalproject.db")
db = sqlite3.connect('finalproject.db', check_same_thread=False)



@app.route("/")
@login_required
def index():
    schedules = db.execute("SELECT id FROM schedule")
    for schedule in schedules:
        participants = db.execute("SELECT user_id FROM participation WHERE schedule_id = ?", schedule["id"])

        if participants:
            db.execute("UPDATE schedule SET participants = ? WHERE id = ? ", len(participants), schedule["id"])
            # db.execute("UPDATE schedule SET participants = ? WHERE id = ? ", schedule["id"])

        else:
            db.execute("UPDATE schedule SET participants = ? WHERE id = ? ", 0, schedule["id"])

    rows = db.execute("SELECT * FROM schedule")
    return render_template("index.html", rows=rows)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        
        username = request.form.get("username")

        # Ensure username was submitted
        if not username:
            flash("Please enter your username")
            return render_template("register.html")

        

        elif db.execute("SELECT * FROM users WHERE username = ?", username):
            flash("invalid username")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter your password")
            return render_template("register.html")

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            flash("Please enter your confirmation password")
            return render_template("register.html")

        if request.form.get("password") == request.form.get("confirmation"):
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                flash("invalid username and/or password")
                return render_template("register.html")


            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            flash('Registerd!')
            return redirect("/")
        else:
            flash("not matching password")
            return render_template("register.html")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter your username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter your password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    elif request.method == "GET":
        return render_template("login.html")

    else :
        flash("Can't log in")
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    flash("log out")
    # Redirect user to login form
    return redirect("/")


@app.route("/setschedule", methods=["GET", "POST"])
@login_required
def setschedule():
    """Get stock quote."""
    if request.method == "POST":
        # Ensure form was submitted
        if not request.form.get("contents"):
            flash("Please enter contents")
            return render_template("setschedule.html")

        if not request.form.get("location"):
            flash("Please enter location")
            return render_template("setschedule.html")

        if not request.form.get("date"):
            flash("Please enter date")
            return render_template("setschedule.html")

        if not request.form.get("start_time"):
            flash("Please enter start time")
            return render_template("setschedule.html")

        if not request.form.get("end_time"):
            flash("Please enter end time")
            return render_template("setschedule.html")

        if db.execute("SELECT contents FROM schedule"):
            conts = db.execute("SELECT contents FROM schedule")
            items = []
            for cont in conts:
                items.append(cont["contents"])

                if request.form.get("contents") in items:
                    flash("Please enter unique contents")
                    return render_template("setschedule.html")

        contents = request.form.get("contents")
        location = request.form.get("location")
        date = request.form.get("date")
        start = request.form.get("start_time")
        end = request.form.get("end_time")
        participants = 0

        db.execute("INSERT INTO schedule (contents, location, date, start_time, end_time, participants) VALUES(?, ?, ?, ?, ?, ?)", contents, location, date, start, end, 0)
        return redirect("/")

    else:
        return render_template("setschedule.html")




@app.route("/participate", methods=["GET", "POST"])
@login_required
def participate():
    """Sell shares of stock"""
    if request.method == "POST":
        # Ensure Symbol was submitted
        if not request.form.get("participate") and not request.form.get("absence"):
            flash("Please enter participate or absence")
            return redirect("/")
            # return render_template("participate.html", rows=rows, participates=participates, absences=absences)

        if request.form.get("participate"):
            if db.execute("SELECT id FROM schedule WHERE contents = ?", request.form.get("participate")):
                participateid = db.execute("SELECT id FROM schedule WHERE contents = ?", request.form.get("participate"))[0]["id"]
                db.execute("INSERT INTO participation (schedule_id, user_id) VALUES(?, ?)", participateid, session["user_id"])

        if request.form.get("absence"):
            if db.execute("SELECT id FROM schedule WHERE contents = ?", request.form.get("absence"))[0]["id"]:
                absenceid = db.execute("SELECT id FROM schedule WHERE contents = ?", request.form.get("absence"))[0]["id"]
                db.execute("DELETE FROM participation WHERE schedule_id = ? AND user_id = ?", absenceid, session["user_id"])


    schedules = db.execute("SELECT id FROM schedule")
    for schedule in schedules:
        participants = db.execute("SELECT user_id FROM participation WHERE schedule_id = ?", schedule["id"],)

        if participants:
            db.execute("UPDATE schedule SET participants = ? WHERE id = ? ", len(participants), schedule["id"])
        else:
            db.execute("UPDATE schedule SET participants = ? WHERE id = ? ", 0, schedule["id"])

    rows = db.execute("SELECT * FROM schedule")

    absences = db.execute("SELECT contents FROM schedule JOIN participation ON schedule.id = participation.schedule_id WHERE user_id = ?", session["user_id"])
    contents = db.execute("SELECT contents FROM schedule")
    participates = [i for i in contents if i not in absences]

    if absences:
        items = []
        for absence in absences:
            items.append(absence['contents'])

        if items:
            return render_template("participate.html", rows=rows, participates=participates, absences=absences, items=items)

        else:
            return render_template("participate.html", rows=rows, participates=participates, absences=absences)

    else:
        return render_template("participate.html", rows=rows, participates=participates, absences=absences)


@app.route("/money", methods=["GET", "POST"])
@login_required
def money():
    assets = db.execute("SELECT * FROM assets")
    liabilities = db.execute("SELECT * FROM liabilities")
    
    liabilities_total = 0
    assets_total = 0
    
    for liabilitie in liabilities:
        liabilities_total += liabilitie["amount"]
    
    for asset in assets:
        assets_total += asset["amount"]
    
    return render_template("money.html", assets=assets, liabilities=liabilities, liabilities_total=liabilities_total, assets_total=assets_total)



@app.route("/setincome", methods=["GET", "POST"])
@login_required
def setincome():
    if request.method == "POST":
        # Ensure form was submitted

        if not request.form.get("amount"):
            flash("Can't set income")
            return render_template("setincome.html")

        if not request.form.get("amount").isdigit():
            flash("Can't set income")
            return render_template("setincome.html")

        if int(request.form.get("amount")) < 1:
            flash("Can't set income")
            return render_template("setincome.html")

        if not request.form.get("date"):
            flash("Please enter a date")
            return render_template("setincome.html")

        if not request.form.get("accounting_title"):
            flash("Can't set income")
            return render_template("setincome.html")


        accounting_title = request.form.get("accounting_title")
        amount = int(request.form.get("amount"))
        date = request.form.get("date")


        db.execute("INSERT INTO assets (accounting_title, amount, date) VALUES(?, ?, ?)", accounting_title, amount, date)

        flash("Set income!")
        return render_template("setincome.html")

    else:
        return render_template("setincome.html")


@app.route("/setexpence", methods=["GET", "POST"])
@login_required
def setexpence():
    if request.method == "POST":
        # Ensure form was submitted

        if not request.form.get("amount"):
            flash("Can't set expence")
            return render_template("setexpence.html")

        if not request.form.get("amount").isdigit():
            flash("Can't set expence")
            return render_template("setexpence.html")

        if int(request.form.get("amount")) < 1:
            flash("Can't set expence")
            return render_template("setexpence.html")

        if not request.form.get("date"):
            flash("Please enter a date")
            return render_template("setexpence.html")

        if not request.form.get("accounting_title"):
            flash("Can't set expence")
            return render_template("setexpence.html")


        accounting_title = request.form.get("accounting_title")
        amount = int(request.form.get("amount"))
        date = request.form.get("date")


        db.execute("INSERT INTO liabilities (accounting_title, amount, date) VALUES(?, ?, ?)", accounting_title, amount, date)

        flash("Set expence!")
        return render_template("setexpence.html")

    else:
        return render_template("setexpence.html")

if __name__ == '__main__':
    app.run(host=os.getenv('APP_ADDRESS', 'localhost'), port=8000)
    # app.run(debug=False, host="0.0.0.0", port=8888 )

