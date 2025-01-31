from secrets                import token_hex
from re                     import match

from flask                  import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session          import Session
from flask_sqlalchemy       import SQLAlchemy
from werkzeug.security      import generate_password_hash, check_password_hash
from werkzeug.exceptions    import HTTPException

from models                 import *
from forms                  import *


# Setup Flask application
app = Flask(__name__)


# Configure flask objects
app.config["SQLALCHEMY_DATABASE_URI"]   = "sqlite:///database.db"
app.config["SESSION_TYPE"]              = "sqlalchemy"
app.config["SESSION_PERMANENT"]         = False
app.config["SESSION_KEY"]               = token_hex(32)
app.config["SECRET_KEY"]                = token_hex(32)


# Setup SQLAlchemy database
db = SQLAlchemy(model_class=Base)
app.config["SESSION_SQLALCHEMY"] = db

db.init_app(app)

with app.app_context():
    db.create_all()


# Setup Flask session
Session(app)


@app.errorhandler(HTTPException)
def error(e):
    """Handles every http execeptions"""
    return render_template("error/error.html", status_code=e.code, error_name=e.name, description=e.description)


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/user", methods=["GET", "POST"])
def user():
    """Show user panel"""

    # Create form object
    form = editForm(username=session["user"], email=session["email"])

    if request.method == "POST":

        # Validate form
        if form.validate():
            update = False
            changes = False
            
            # Get form data
            username = form.username.data
            email = form.email.data
            password = form.password.data

            stmt = db.select(User.username, User.email, User.password).where(User.username == session["user"])
            user = db.session.execute(stmt).first()

            # Verify if username exists only if current username is different of session username
            if session["user"] != username:
                stmt = db.select(User).where(User.username == username)
                if db.session.execute(stmt).first():
                    return jsonify({"message": "Username already exists!"}), 400
                update = True

            # Verify if email exists only if current email is different of session email
            if session["email"] != email:
                stmt = db.select(User).where(User.email == email)
                if db.session.execute(stmt).first():
                    return jsonify({"message": "Email already exists!"}), 400
                update = True

            if not password and update:
                stmt = db.update(User).where(User.username == user[0]).values(
                    username=username,
                    email=email
                )
                changes = True
            elif password:
                if 3 < len(password) < 129: 
                    stmt = db.update(User).where(User.username == user[0]).values(
                        username=username,
                        email=email,
                        password=generate_password_hash(password)
                    )
                    changes = True
                else:
                    return jsonify({"message": "New password must be in 3 to 128 characters!"}), 400
      
            # Update databse only if have changes
            if changes:
                db.session.execute(stmt)
                db.session.commit()

                session["user"] = username
                session["email"] = email

                return jsonify({"message": "success"}), 200

            return jsonify({"message": "Nothing changed."}), 200
        else:
            # Return always the first error
            return jsonify({"message": list(form.errors.values())[0][0]}), 400


    return render_template("user/index.html", form=form, delForm=deleteForm(), username=session["user"], email=session["email"])


@app.route("/user/delete", methods=["POST"])
def delete_account():
    """Delete user account"""

    # Create form object
    form = deleteForm()

    # Validate delete account form
    if form.validate():
        
        # Get form data
        password = form.password.data

        # Get user id and password
        stmt = db.select(User.id, User.password).where(User.username == session["user"])
        user = db.session.execute(stmt).first()

        # Verify if password hashes
        if check_password_hash(user[1], password):
            db.session.execute(db.delete(User).where(User.id == user[0]))
            db.session.commit()

            return jsonify({"message": "success"}), 200
        else:
            return jsonify({"message": "Wrong password!"}), 400

    # Return always the first error
    return jsonify({"message": list(form.errors.values())[0][0]}), 400


@app.route("/user/cart")
def cart():
    return render_template("user/index.html", username=session["user"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login users into application"""

    # Create form object
    form = LoginForm()

    if request.method == "POST":
        
        # Validate form
        if form.validate():

            # Get form data
            email = form.email.data
            password = form.password.data

            # Get user data
            stmt = db.select(User.username, User.password).where(User.email == email)
            user = db.session.execute(stmt).first()

            # Checks user existence and password
            if user is None or not check_password_hash(user[1], password):
                return jsonify({"message": "Wrong email or password!"}), 400

            # Create current user session
            session["user"] = user[0]
            session["email"] = email

            return jsonify({"message": "success"}), 200
        else:
            # Return always the first error
            return jsonify({"message": list(form.errors.values())[0][0]}), 400

    return render_template("login/login.html", form=form)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """Create new user account into application"""

    # Create form object
    form = RegisterForm()
    
    if request.method == "POST":

        # Validate form
        if form.validate():
            
            # Get form data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            confirmation = form.confirmation.data

            # Verify if username exists
            stmt = db.select(User).where(User.username == username)
            if db.session.execute(stmt).first():
                return jsonify({"message": "Username already exists!"}), 400

            # Verify if email exists
            stmt = db.select(User).where(User.email == email)
            if db.session.execute(stmt).first():
                return jsonify({"message": "Email already exists!"}), 400

            # Ensures that passwords are equal
            if password != confirmation:
                return jsonify({"message": "Passwords don't match!"}), 400

            # Create and add new user in database
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )

            db.session.add(new_user)
            db.session.commit()

            # Create current user session
            session["user"] = username
            session["email"] = email
            
            return jsonify({"message": "success"}), 200
        else:
            # Return always the first error
            return jsonify({"message": list(form.errors.values())[0][0]}), 400

    return render_template("login/create_account.html", form=form)


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

