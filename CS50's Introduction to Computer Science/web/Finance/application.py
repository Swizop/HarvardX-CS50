import os

from sqlalchemy import create_engine, engine, exc, select, insert, update, desc, and_
from sqlalchemy import Table, Column, MetaData
import sqlalchemy
from sqlalchemy.sql import text

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask.helpers import url_for
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy.util.langhelpers import symbol
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database w/ sqlalchemy
db = 'sqlite:///finance.db'

# Make sure API key is set
# If not set, run: set API_KEY=...
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userId = session["user_id"]
    # OLD: holdings = db.execute("SELECT * FROM holdings WHERE user_id = ?", userId)
    # NEW:
    engine = create_engine(db)
    meta = MetaData()
    conn = engine.connect()

    holdings = Table('holdings', meta, autoload=True, autoload_with=engine)
    hd = select([holdings]).where(holdings.c.user_id==userId)
    hrows = conn.execute(hd).fetchall()


    users = Table('users', meta, autoload=True, autoload_with=engine)
    # cash = float(db.execute("SELECT * FROM users WHERE id = ?", userId)[0]["cash"])
    cash = float(conn.execute(select([users]).where(users.c.id==userId)).fetchall()[0]["cash"])

    conn.close()
    engine.dispose()
    stocksValue = 0
    if not hrows:
        return render_template("index.html", er = 1, cash = cash)
    else:
        companyNames = []
        currentPrices = []
        for h in hrows:
            obj = lookup(h["symbol"])
            companyNames.append(obj["name"])
            currentPrices.append(obj["price"])
            stocksValue += float(obj["price"]) * int(h["amount"])
        stocksValue = usd(stocksValue + cash)
        cash = usd(cash)
        return render_template("index.html", holdings = hrows, companyNames = companyNames, currentPrices = currentPrices, cash = cash, stocksValue = stocksValue)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol").strip().upper()
        obj = lookup(symbol)
        if not obj:
            return render_template("buy.html", er = 1)
        shares = request.form.get("shares").strip()
        if not shares.isnumeric():
            return render_template("buy.html", er = 2)
        
        price = float(obj["price"])
        userId = session["user_id"]

        engine = create_engine(db)
        meta = MetaData()
        conn = engine.connect()

        users = Table('users', meta, autoload=True, autoload_with=engine)
        acquisitions = Table('acquisitions', meta, autoload=True, autoload_with=engine)
        holdings = Table('holdings', meta, autoload=True, autoload_with=engine)
        

        userBalance = float(conn.execute(select([users]).where(users.c.id==userId)).fetchall()[0]["cash"])

        if price * int(shares) > userBalance:
            return render_template("buy.html", er = 3)

        shares = int(shares)
        #OLD:
        #   db.execute("INSERT INTO acquisitions (user_id, symbol, amount, price) VALUES(?, ?, ?, ?)", userId, symbol, shares, price)
        #NEW:
        ins = acquisitions.insert().values(user_id = userId, symbol = symbol, amount = shares, price = price)
        result1 = conn.execute(ins)

        #OLD:
        #   db.execute("UPDATE users SET cash = ? WHERE id = ?", userBalance - price * shares, userId)
        #NEW:
        usex = users.update().values(cash=users.c.cash - price * shares).where(users.c.id == userId)
        conn.execute(usex)

        #OLD:
        #   db.execute("INSERT INTO holdings (user_id, symbol, amount, average_price) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, symbol) DO UPDATE SET average_price = (average_price * amount + ? * ?) / (amount + ?), amount = amount + ?",\
             #userId, symbol, shares, price,\
                #shares, price, shares, shares )
        #NEW:
        ins = holdings.insert().values(user_id = userId, symbol = symbol, amount = shares, average_price = price)
        try:
            conn.execute(ins)
        except sqlalchemy.exc.IntegrityError:           #ON CONFLICT
            hex = holdings.update().values(average_price=(holdings.c.average_price * holdings.c.amount + shares * price) / (holdings.c.amount + shares), amount=holdings.c.amount + shares)\
                .where(and_(holdings.c.user_id == userId, holdings.c.symbol == symbol))
            conn.execute(hex)

        conn.close()
        engine.dispose()
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userId = session["user_id"]
    #OLD: history = db.execute("SELECT * FROM acquisitions WHERE user_id = ? ORDER BY acquisition_date DESC", userId)
    #NEW:
    engine = create_engine(db)
    meta = MetaData()
    conn = engine.connect()

    acquisitions = Table('acquisitions', meta, autoload=True, autoload_with=engine)
    asel = select([acquisitions]).where(acquisitions.c.user_id==userId).order_by(desc(acquisitions.c.acquisition_date))
    history = conn.execute(asel).fetchall()

    conn.close()
    engine.dispose()
    if not history:
        return redirect("/")
    return render_template("history.html", history = history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        engine = create_engine(db)
        meta = MetaData()
        conn = engine.connect()
        users = Table('users', meta, autoload=True, autoload_with=engine)
        s = select([users]).where(users.c.username==request.form.get("username"))
        rows = conn.execute(s).fetchall()
        conn.close()
        engine.dispose()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol").strip().upper()
        obj = lookup(symbol)
        if obj:
            return render_template("quoted.html", symbol=symbol, obj = obj)
        else:
            return render_template("quote.html", er = 1)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("register.html", blank = 1)
        if not password:
            return render_template("register.html", blank = 2)
        if not request.form.get("confirmation"):
            return render_template("register.html", blank = 3)
        if request.form.get("confirmation") != password:
            return render_template("register.html", blank = 4)
        
        #OLD: userQuery = db.execute("SELECT * FROM users WHERE username = ?", username)
        #NEW:
        engine = create_engine(db)
        meta = MetaData()
        conn = engine.connect()

        users = Table('users', meta, autoload=True, autoload_with=engine)
        usel = select([users]).where(users.c.username == username)
        rows = conn.execute(usel).fetchall()

        if rows:
            return render_template("register.html", blank = 5)

        # db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
        conn.execute(users.insert().values(username = username, hash = generate_password_hash(password)))

        conn.close()
        engine.dispose()
        return redirect("/")
    


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        engine = create_engine(db)
        meta = MetaData()
        conn = engine.connect()
        holdings = Table('holdings', meta, autoload=True, autoload_with=engine)
        userId = session["user_id"]
        # holdings = db.execute("SELECT * FROM holdings WHERE user_id = ?", userId)

        hd = select([holdings]).where(holdings.c.user_id==userId)
        hrows = conn.execute(hd).fetchall()
        try:
            er = int(request.args.get("er"))                                            #GET parameter sent from a bad POST request
        except TypeError:
            er = None
        if not hrows:
            return redirect("/")
        conn.close()
        engine.dispose()
        return render_template("sell.html", holdings = hrows, er = er)

    else:
        engine = create_engine(db)
        meta = MetaData()
        conn = engine.connect()
        holdings = Table('holdings', meta, autoload=True, autoload_with=engine)

        symbol = request.form.get("symbol")
        shares = request.form.get("shares").strip()
        userId = session["user_id"]
        if not shares.isnumeric():
            return redirect(url_for("sell", er = 2))

        # holding = db.execute("SELECT * FROM holdings WHERE user_id = ? AND symbol = ?", userId, symbol)
        hd = conn.execute(select([holdings]).where(and_(holdings.c.user_id==userId, holdings.c.symbol == symbol))).fetchall()
        owned = int(hd[0]["amount"])
        shares = int(shares)
        if not hd or shares > owned:           #if the user submits the name of a stock he doesn't own or if he requests more shares than he has in his acc
            conn.close()
            engine.dispose()
            return redirect(url_for("sell", er = 3))

        price = lookup(symbol)["price"]
        # db.execute("INSERT INTO acquisitions (user_id, symbol, amount, price, type) VALUES (?, ?, ?, ?, 'sell')", userId, symbol, shares, price)

        acquisitions = Table('acquisitions', meta, autoload=True, autoload_with=engine)
        conn.execute(acquisitions.insert().values(user_id = userId, symbol = symbol, amount = shares, price = price, type = 'sell'))


        # db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", price * shares, userId)
        users = Table('users', meta, autoload=True, autoload_with=engine)
        conn.execute(users.update().values(cash=users.c.cash + price * shares).where(users.c.id == userId))

        print(shares, owned)
        if shares == owned:
            #db.execute("DELETE FROM holdings WHERE user_id = ? AND symbol = ?", userId, symbol)
            holdings = Table('holdings', meta, autoload=True, autoload_with=engine)
            conn.execute(holdings.delete().where(and_(holdings.c.user_id == userId, holdings.c.symbol == symbol)))
        else:
            # db.execute("UPDATE holdings SET amount = amount - ? WHERE user_id = ? AND symbol = ?", shares, userId, symbol)
            holdings = Table('holdings', meta, autoload=True, autoload_with=engine)
            conn.execute(holdings.update().values(amount=holdings.c.amount - shares).where(and_(holdings.c.user_id == userId, holdings.c.symbol == symbol)))

        conn.close()
        engine.dispose()
        return redirect("/")



@app.route("/nasdaq")                   #helper route to generate dynamic suggestions for input
def nasdaq():
    q = request.args.get("q")
    if q:
        #OLD: stocks = db.execute("SELECT * FROM nasdaq WHERE symbol LIKE ?", q.upper() + "%")[:5] rows[0]["hash"]
        #NEW:
        engine = create_engine(db)
        meta = MetaData()
        conn = engine.connect()

        nasdaq = Table('nasdaq', meta, autoload=True, autoload_with=engine)
        q = q.upper() + "%"
        nsel = select([nasdaq]).where(nasdaq.c.symbol.like(q))
        rows = conn.execute(nsel).fetchall()
        stocks = []
        x = 0
        for row in rows:
            stocks.append({"symbol": row["symbol"]}) # or simply data.append(list(row))
            x += 1
            if x == 5:
                break
    else:
        stocks = []
    conn.close()
    engine.dispose()
    return jsonify(stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run(debug=True)