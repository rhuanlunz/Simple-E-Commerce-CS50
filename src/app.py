from secrets            import token_hex
from re                 import match

from flask              import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session      import Session
from flask_sqlalchemy   import SQLAlchemy
from flask_bcrypt       import Bcrypt

from models             import *


# Setup Flask application
app = Flask(__name__)


# Configure flask objects
app.config["SQLALCHEMY_DATABASE_URI"]   = "sqlite:///database.db"
app.config["SESSION_TYPE"]              = "sqlalchemy"
app.config["SESSION_PERMANENT"]         = False
app.config["SESSION_KEY"]               = token_hex(32)


# Setup SQLAlchemy database
db = SQLAlchemy(model_class=Base)
app.config["SESSION_SQLALCHEMY"] = db

db.init_app(app)

with app.app_context():
    db.create_all()


# Setup Flask session
Session(app)


# Setup Flask Bcrypt
bcrypt = Bcrypt(app)


@app.route("/")
def index():
    return f"Logged as {session["user"]}"


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login users into application"""

    if request.method == "POST":
        # Get request data
        data = request.get_json()

        email = data["email"]
        password = data["password"]

        # Ensures that data was submitted
        if not email or not password:
            return jsonify({"message": "Missing input fields!"}), 400

        # Validate email
        if not match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            return jsonify({"message": "Invalid email!"}), 400

        # Get user data
        stmt = db.select(User.username, User.password).where(User.email == email)
        user = db.session.execute(stmt).first()

        # Checks user existence and password
        if user is None or not bcrypt.check_password_hash(user[1], password):
            return jsonify({"message": "Wrong email or password!"}), 400

        # Create current user session
        session["user"] = user[0]

        return jsonify({"message":"success"}), 200

    return render_template("login/login.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """Create new user account into application"""

    if request.method == "POST":
        # Get request data
        data = request.get_json()

        username = data["username"]
        email = data["email"]
        password = data["password"]
        confirmation = data["confirmation"]

        # Verify input sizes
        if len(username) > 30 or len(email) > 254 or len(password) > 128:
            return jsonify({"message": "Data length is too high!"}), 400

        # Ensures that data was submitted
        if not username or not email or not password or not confirmation:
            return jsonify({"message": "Missing input fields!"}), 400

        # Validate email
        if not match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            return jsonify({"message": "Invalid email!"}), 400

        # Ensures that passwords are equal
        if password != confirmation:
            return jsonify({"message": "Passwords don't match!"}), 400

        # Verify if username exists
        stmt = db.select(User).where(User.username == username)

        # Redirect if username exists
        if db.session.execute(stmt).first():
            return jsonify({"message": "Username already exists!"}), 400

        # Verify if email is registred
        stmt = db.select(User).where(User.email == email)

        # Redirect if email exists
        if db.session.execute(stmt).first():
            return jsonify({"message": "Email already exists!"}), 400

        # Create and add new user in database
        new_user = User(
            username=username,
            email=email,
            password=bcrypt.generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        # Create current user session
        session["user"] = username

        return jsonify({"message":"success"}), 200

    return render_template("login/create_account.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    return render_template("login/forgot.html")


@app.route("/logout")
def logout():
    """Logout user current session"""
    session.clear()
    return redirect(url_for("login"))


if __name__=="__main__":
    app.run(debug=True)

