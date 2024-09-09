from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, request, session, current_app, abort, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from helpers import apology, login_required
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.exc import OperationalError
from flask_migrate import Migrate
from flask_caching import Cache
from flask_ckeditor import CKEditor
from wtforms import TextAreaField, StringField, DateTimeField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES

# Configure application
app = Flask(__name__, static_folder='static', static_url_path='/static')
with app.app_context():
    # within this block, current_app points to app.
    print(current_app.name)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="shorla",
    password="123qweasZ,",
    hostname="shorla.mysql.pythonanywhere-services.com",
    databasename="shorla$calculator",
)
engine = create_engine('mysql+mysqlconnector://shorla:123qweasZ,@shorla.mysql.pythonanywhere-services.com/shorla$calculator?charset=utf8mb4')
images = UploadSet('images', IMAGES)


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SECRET_KEY'] = "dev"
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads/images'
upload_dir = os.path.join(app.root_path, app.config['UPLOADED_IMAGES_DEST'])
print(f"Attempting to create directory: {upload_dir}")
os.makedirs(upload_dir, exist_ok=True)
configure_uploads(app, images)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class SecureModelView(ModelView):
    def is_accessible(self):
        user_id = session.get("user_id")
        user = User.query.filter_by(id=user_id).first()
        if user and user.is_admin:
            return True
        else:
            abort(403)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_filename = db.Column(db.String(255))
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    image_filename = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only.')])
    content = CKTextAreaField('Content')
    author = StringField('Author', validators=[DataRequired()])
    date_posted = DateTimeField('Date Posted', default=datetime.utcnow)
    slug = StringField('Slug', validators=[DataRequired()])

def save_uploaded_file(field, filename):
    try:
        upload_dir = app.config['UPLOADED_IMAGES_DEST']
        os.makedirs(upload_dir, exist_ok=True)
        field.data.save(os.path.join(upload_dir, filename))
    except Exception as e:
        print(f"Error saving file: {e}")
        flash("Error saving file. Please try again.", "error")

class PostModel(SecureModelView):
    form = PostForm
    create_template = 'edit.html'
    edit_template = 'edit.html'

    def on_model_change(self, form, model, is_created):
        # Save the image file using Flask-Uploads
        if 'image_filename' in request.files:
            image_file = request.files['image_filename']
            if image_file.filename:
                model.image_filename = images.save(image_file)
        # If no new file is uploaded, retain the existing image file
        elif model.image_filename:
            form.image_filename.data = model.image_filename

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, ForeignKey("users.user_id"), nullable=False)

admin = Admin(app, index_view=AdminIndexView(name='Admin'))
admin.add_view(PostModel(Posts, db.session))
admin.add_view(SecureModelView(User, db.session))

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    hash = db.Column(db.String(255), nullable=False)

    # create a string
    def __repr__(self):
        return '<Name %r>' % self.username

class check_length(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    length = db.Column(db.Numeric, nullable=False)
    sum = db.Column(db.Numeric, nullable=False)

class data(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    birthdate = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    gender = db.Column(db.String(255), nullable=False)
    hair_state = db.Column(db.String(255), nullable=False)

class hair_data(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    measurement = db.Column(db.Numeric, nullable=False)

class average_data(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    average = db.Column(db.Float, nullable=False)

def redirect_url(default='index'):
    return request.args.get('next') or url_for(default)

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
    all_posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    latest_three_posts = all_posts[:3]
    return render_template("index.html", posts=latest_three_posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/blog")
def blog():
    all_posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    return render_template("blog.html", posts=all_posts)

@app.route("/post/<string:slug>")
def post(slug):
    post = Posts.query.filter_by(slug=slug).one()
    return render_template("post.html", post=post)

@app.route('/upload', methods=['POST'])
def upload():
    form = PostForm()

    if form.validate_on_submit():
        filename = secure_filename(form.image_filename.data.filename)

        # Save the uploaded file and get the correct filename
        filename = save_uploaded_file(form.image_filename, filename)

        # Assuming you have a post instance, update the image filename
        # Replace `post` with the actual instance of your Post model
        post.image_filename = filename

        # Commit changes to the database
        db.session.commit()

        flash('File uploaded successfully.', 'success')
    else:
        flash('File upload failed. Please try again.', 'error')

    return redirect(url_for('index'))

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Posts.query.get_or_404(post_id)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        if 'image_filename' in request.files:
            image_file = request.files['image_filename']
            if image_file.filename:
                filename = secure_filename(image_file.filename)
                save_uploaded_file(image_file, filename)
                post.image_filename = filename

        form.populate_obj(post)
        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('post', slug=post.slug))

    return render_template('edit.html', form=form, post=post)

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

        if data.query.filter_by(email=email).first():
            return apology("Email already exists", 400)

        users = Users(firstname=firstname, lastname=lastname, username=username, hash=pwhash)
        info = data(email=email, gender=gender, birthdate=birthdate, hair_state=hairstate)
        # Insert username and pwhash into database for regular user
        try:
            db.session.add_all([users, info])
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return apology("Internal Server Error", 500)

        # Assuming you have an 'admin' role in your User model
        admin = User(name=username, is_admin=False, user_id=users.user_id)

        # Insert admin user into database
        try:
            db.session.add(admin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

        # Redirect user to calculation page with form data if present
        if 'form_data' in session:
            return redirect(url_for('calculator_get'))

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
        username = request.form.get("username")
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = Users.query.filter_by(username=username).all()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
                rows[0].hash, request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0].user_id
        next_url = request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for("index"))

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

@app.route('/calculator', methods=['GET'])
@cache.cached(timeout=60)
def calculator_get():
    # Check if the user is logged in by retrieving user_id from session
    user_id = session.get("user_id")
    if user_id is None:
        # If not logged in, initialize default values and render the form
        date = 0
        sum = 0
        length = 0
        fourthmonth = 0
        average_growth = 0
        return render_template("calculator.html", sum=sum, date=date, length=length, fourthmonth=fourthmonth, average_growth=average_growth)

    data1 = db.session.query(average_data).filter_by(user_id=user_id).order_by(average_data.date.desc()).first()
    if data1:
        fourthmonth = data1.date
        average_growth = data1.average
    else:
        fourthmonth = 0
        average_growth = 0

    data2 = db.session.query(check_length).filter_by(user_id=user_id).order_by(check_length.date.desc()).first()
    if data2:
        length = data2.length
        sum = data2.sum
    else:
        length = 0
        sum = 0
    return render_template("calculator.html",sum=sum, length=length,  fourthmonth=fourthmonth, average_growth=average_growth)


@app.route('/calculator', methods=['POST'])
def calculator_post():
    user_id = session.get("user_id")
    if not user_id:
        next_url = url_for('calculator_get', **request.form.to_dict(flat=True))
        flash("Please log in to continue with the calculation.", "warning")
        return redirect(url_for('login', next=next_url))

    firstmonth = request.form.get("firstmonth")
    if not firstmonth:
        return "must provide date", 400
    f_measurement = float(request.form.get("f-measurement"))
    if not f_measurement:
        return "must provide measurement", 400
    secondmonth = request.form.get("secondmonth")
    if not secondmonth:
        return "must provide date", 400
    s_measurement = float(request.form.get("s-measurement"))
    if not s_measurement:
        return "must provide measurement", 400
    thirdmonth = request.form.get("thirdmonth")
    if not thirdmonth:
        return "must provide date", 400
    t_measurement = float(request.form.get("t-measurement"))
    if not t_measurement:
        return "must provide measurement", 400
    fourthmonth = request.form.get("fourthmonth")
    if not fourthmonth:
        return "must provide date", 400
    fo_measurement = float(request.form.get("fo-measurement"))
    if not fo_measurement:
        return "must provide measurement", 400

    f1 = s_measurement - f_measurement
    f2 = t_measurement - s_measurement
    f3 = fo_measurement - t_measurement
    sum = f1 + f2 + f3
    average_growth = round(sum / 3, 2)

    firstmonth_date = datetime.strptime(firstmonth, "%Y-%m-%d")
    secondmonth_date = datetime.strptime(secondmonth, "%Y-%m-%d")
    thirdmonth_date = datetime.strptime(thirdmonth, "%Y-%m-%d")
    fourthmonth_date = datetime.strptime(fourthmonth, "%Y-%m-%d")

    # Assuming hair_data and average_data are SQLAlchemy models
    firstmonth_hair_data = hair_data(user_id=user_id, date=firstmonth_date, measurement=f_measurement)
    secondmonth_hair_data = hair_data(user_id=user_id, date=secondmonth_date, measurement=s_measurement)
    thirdmonth_hair_data = hair_data(user_id=user_id, date=thirdmonth_date, measurement=t_measurement)
    fourthmonth_hair_data = hair_data(user_id=user_id, date=fourthmonth_date, measurement=fo_measurement)
    info = average_data(user_id=user_id, date=fourthmonth_date, average=average_growth)

    try:
        db.session.merge(firstmonth_hair_data)
        db.session.merge(secondmonth_hair_data)
        db.session.merge(thirdmonth_hair_data)
        db.session.merge(fourthmonth_hair_data)
        db.session.merge(info)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return "Internal Server Error", 500

    return render_template("calculator.html", fourthmonth=fourthmonth, average_growth=average_growth)



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
        data = db.session.query(average_data).order_by(average_data.user_id.desc()).limit(1)
        length = db.session.query(hair_data).order_by(hair_data.user_id.desc()).limit(1)

        length = length[0].measurement
        up_date = data[0].date
        average = data[0].average
        row = db.session.query(check_length).order_by(check_length.user_id.desc()).limit(1)
        if row.count() != 1:
            try:
                date_1 = parse_date(date)
                date_2 = up_date
                result = subtract_dates(date_1, date_2)
            except ValueError as e:
                error_message = str(e)
            sum = round((result * float(average)) + float(length), 2)
        else:
            date2 = row[0].date
            length2 = row[0].length
            try:
                date_1 = parse_date(date)
                date_3 = parse_date(date2)
                result = subtract_dates(date_1, date_3)
            except ValueError as e:
                error_message = str(e)

            sum = round((result * average) + length2, 2)

            input_data = check_length(user_id=user_id, date=date, length=n_measurement, sum=sum)
            try:
                db.session.add(input_data)
                db.session.commit()

            except OperationalError as e:
                print(f"OperationalError: {e}")
                return apology("Database Connection Error", 500)

        data1 = db.session.query(average_data).order_by(average_data.user_id.desc()).limit(1)
        if data1.count() == 1:
            fourthmonth = data1[0].date
            average_growth = data1[0].average
        else:
            fourthmonth = 0
            average_growth = 0

        return render_template("calculator.html", sum=sum, date=date, length=n_measurement, fourthmonth=fourthmonth, average_growth=average_growth)

if __name__ == '__main__':
    app.run()
