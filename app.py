from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, request, session, current_app
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from helpers import apology, login_required


# Configure application
app = Flask(__name__)
with app.app_context():
    # within this block, current_app points to app.
    print (current_app.name)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="shorla",
    password="123qweasZ,",
    hostname="shorla.mysql.pythonanywhere-services.com",
    databasename="shorla$calculator",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SECRET_KEY'] = "dev"

db = SQLAlchemy(app)
admin = Admin(app)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime)
    slug = db.Column(db.String(255))

admin.add_view(ModelView(Posts, db.session))

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def subtract_dates(date1, date2):
    year_diff = date1.year - date2.year
    month_diff = date1.month - date2.month
    total_month_diff = year_diff * 12 + month_diff
    return float(abs(total_month_diff))

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    posts = Posts.query.all()
    return render_template("index.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/blog")
def blog():
    posts = Posts.query.all()
    return render_template("blog.html", posts=posts)


@app.route("/post/<string:slug>")
def post(slug):
    post = Posts.query.filter_by(slug=slug).one()
    return render_template("post.html", post=post)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)
        firstname = request.form.get("firstname")
        if not firstname:
            return apology("must provide firstname", 400)
        lastname = request.form.get("lastname")
        if not lastname:
            return apology("must provide lastname", 400)
        email = request.form.get("email")
        if not email:
            return apology("must provide email", 400)
        gender = request.form.get("gender")
        if not gender:
            return apology("must provide Gender", 400)
        hairstate = request.form.get("hairstate")
        if not hairstate:
            return apology("must provide hairstate", 400)
        birthdate = request.form.get("birthdate")
        if not birthdate:
            return apology("must provide Date of Birth", 400)
        password = request.form.get("password")
        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must repeat password", 400)
        # Ensure both passwords match
        if password != confirmation:
            return apology("passwords don't match", 400)
        # hash user's password
        pwhash = generate_password_hash(password, method="scrypt", salt_length=16)

        # Insert username and pwhash into database
        try:
            db.execute(
                "INSERT INTO users(firstname, lastname, username,  hash) VALUES(?,?,?,?)",firstname, lastname, username, pwhash
            )
            db.execute(
                "INSERT INTO data(email, gender, birthdate, hairstate) VALUES(?,?,?,?)",email, gender, birthdate, hairstate
            )
        except:
            return apology("User already exist")
        return render_template("login.html")
    else:
        return render_template("signup.html")
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]

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

@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    if request.method == "GET":
         # get user id
        user_id = session["user_id"]
        data = db.execute(
                "SELECT date, average FROM average_data WHERE user_id = ? ORDER BY rowid DESC LIMIT 1",user_id
            )
        if len(data) == 1:
            fourthmonth = data[0]["date"]
            average_growth = data[0]["average"]
        else:
            fourthmonth = 0
            average_growth = 0
        row = db.execute(
                "SELECT date, sum, length FROM check_length WHERE user_id = ? ORDER BY rowid DESC LIMIT 1",user_id
            )
        if len(row)== 1:
            date = row[0]["date"]
            sum = row[0]["sum"]
            length = row[0]["length"]
        else:
            date =0
            sum = 0
            length = 0
        return render_template("calculator.html", fourthmonth = fourthmonth, average_growth = average_growth, sum = sum, date = date, length = length)
    else:
        # get user id
        user_id = session["user_id"]
        firstmonth = request.form.get("firstmonth")
        if not firstmonth:
            return apology("must provide date", 400)
        f_measurement = float(request.form.get("f-measurement"))
        if not f_measurement:
            return apology("must provide measurement", 400)
        secondmonth = request.form.get("secondmonth")
        if not secondmonth:
            return apology("must provide date", 400)
        s_measurement = float(request.form.get("s-measurement"))
        if not s_measurement:
            return apology("must provide measurement", 400)
        thirdmonth = request.form.get("thirdmonth")
        if not thirdmonth:
            return apology("must provide date", 400)
        t_measurement = float(request.form.get("t-measurement"))
        if not t_measurement:
            return apology("must provide measurement", 400)
        fourthmonth = request.form.get("fourthmonth")
        if not fourthmonth:
            return apology("must provide date", 400)
        fo_measurement = float(request.form.get("fo-measurement"))
        if not fo_measurement:
            return apology("must provide measurement", 400)
        sum = fo_measurement - f_measurement
        average_growth = round(sum / 3, 2)

        try:
            db.execute(
                "INSERT INTO hair_data(user_id, date, measurement) VALUES(?,?,?)",user_id, firstmonth, f_measurement
            )
            db.execute(
                "INSERT INTO hair_data(user_id, date, measurement) VALUES(?,?,?)",user_id, secondmonth, s_measurement
            )
            db.execute(
                "INSERT INTO hair_data(user_id, date, measurement) VALUES(?,?,?)",user_id, thirdmonth, t_measurement
            )
            db.execute(
                "INSERT INTO hair_data(user_id, date, measurement) VALUES(?,?,?)",user_id, fourthmonth, fo_measurement
            )
            db.execute(
                "INSERT INTO average_data(user_id, date, average) VALUES(?,?,?)",user_id, fourthmonth, average_growth
            )
        except:
            return apology(" missing data")
            raise
        return render_template("calculator.html", fourthmonth = fourthmonth, average_growth = average_growth)


@app.route("/calculator_main", methods=["GET", "POST"])
@login_required
def calculator_main():
    result = 0
    error_message = None
    if request.method == "POST":
        user_id = session["user_id"]
        date = request.form.get("d-month")
        if not date:
            return apology("must provide date", 400)
        n_measurement = float(request.form.get("n-measurement"))
        if not n_measurement:
            return apology("must provide measurement", 400)
        data = db.execute(
                "SELECT date, average FROM average_data WHERE user_id = ? ORDER BY rowid DESC LIMIT 1",user_id
            )
        length = db.execute(
                "SELECT measurement FROM hair_data WHERE user_id = ? ORDER BY rowid DESC LIMIT 1",user_id
            )
        length = length[0]["measurement"]
        up_date = data[0]["date"]
        average = data[0]["average"]
        row = db.execute(
                "SELECT date, length FROM check_length WHERE user_id = ? ORDER BY rowid DESC LIMIT 1",user_id
            )
        if len(row)!= 1:
            try:
                date_1 = parse_date(date)
                date_2 = parse_date(up_date)
                result = subtract_dates(date_1, date_2)
            except ValueError as e:
                error_message = str(e)
            sum = round((result * average) + length,2)
        else:
            date2 = row[0]["date"]
            length2 = row[0]["length"]
            try:
                date_1 = parse_date(date)
                date_3 = parse_date(date2)
                result = subtract_dates(date_1, date_3)
            except ValueError as e:
                error_message = str(e)

            sum = round((result * average) + length2, 2)
        try:
            db.execute(
                "INSERT INTO check_length(user_id, date, length, sum) VALUES(?,?,?,?)",user_id, date, n_measurement, sum
            )
        except:
            return apology(" missing data")
        data1 = db.execute(
                "SELECT date, average FROM average_data WHERE user_id = ? ORDER BY rowid DESC LIMIT 1",user_id
            )
        if len(data1) == 1:
            fourthmonth = data1[0]["date"]
            average_growth = data1[0]["average"]
        else:
            fourthmonth = 0
            average_growth = 0
        return render_template("calculator.html", sum = sum, date = date, length = n_measurement, fourthmonth = fourthmonth, average_growth = average_growth)

if __name__ == '__main__':
    app.run()