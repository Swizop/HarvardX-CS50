import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
#cmd python -m flask run in order to run web app

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")

def is_valid_date(month, day):
    day_count_for_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # if year%4==0 and (year%100 != 0 or year%400==0):
    #     day_count_for_month[2] = 29
    return (1 <= month <= 12 and 1 <= day <= day_count_for_month[month])

def is_valid_name(string):
    r = False
    for c in string:
        if c.isalpha():
            r = True
        elif c != " ":
            return False
    return r

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        month = request.form.get("month")
        day = request.form.get("day")
        name = request.form.get("name")

        if month.isnumeric() and day.isnumeric() and is_valid_name(name) and is_valid_date(int(month), int(day)):
            db.execute("INSERT INTO birthdays (name, month, day) VALUES(?, ?, ?)", name, month, day)

        return redirect("/")

    else:

        birthdays = db.execute("SELECT * FROM birthdays")

        return render_template("index.html", birthdays = birthdays)



@app.route("/delete", methods=["GET", "POST"])
def delete():
    db.execute("DELETE FROM birthdays WHERE id = ?", request.form.get("id"))
    return redirect("/")
