from secrets                import token_hex

from flask                  import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session          import Session
from flask_sqlalchemy       import SQLAlchemy
from werkzeug.security      import generate_password_hash, check_password_hash
from werkzeug.exceptions    import HTTPException
from functools              import wraps

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
    Products().initialize(db.session)


# Setup Flask session
Session(app)


@app.errorhandler(HTTPException)
def error(e):
    """ Handles every http execeptions """
    return render_template("error/index.html", status_code=e.code, error_name=e.name, description=e.description)


def login_required(view):
    @wraps(view)
    def wrapper(**kwargs):
        if session.get("user") is None and session.get("email") is None:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapper


def login_required_api(view):
    @wraps(view)
    def wrapper(**kwargs):
        if session.get("user") is None and session.get("email") is None:
            return jsonify({"type": "error", "message": "You need to login!"}), 401
        return view(**kwargs)
    return wrapper


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("shop"))


@app.route("/shop", methods=["GET"])
def shop():
    """ Get and show all products in database """

    data = db.session.query(Products).all()

    products = [i for i in data]

    return render_template("shop/index.html", products=products, session=session.get("user"))


@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    """ Show user panel """

    # Create form object
    form = editForm(username=session.get("user"), email=session.get("email"))

    if request.method == "POST":

        # Validate form
        if form.validate():
            update = False
            changes = False
            
            # Get form data
            username = form.username.data
            email = form.email.data
            password = form.password.data

            user = db.session.query(User).filter_by(username=session.get("user"), email=session.get("email")).first()

            # Verify if username exists only if current username is different of session username
            if user.username != username:
                if db.session.query(User).filter_by(username=username).first():
                    return jsonify({"type": "error", "message": "Username already exists!"}), 400
                update = True

            # Verify if email exists only if current email is different of session email
            if user.email != email:
                if db.session.query(User).filter_by(email=email).first():
                    return jsonify({"type": "error", "message": "Email already exists!"}), 400
                update = True

            if not password and update:
                stmt = db.update(User).where(User.username == user.username).values(
                    username=username,
                    email=email
                )
                changes = True
            elif password:
                if 3 < len(password) < 129: 
                    stmt = db.update(User).where(User.username == user.username).values(
                        username=username,
                        email=email,
                        password=generate_password_hash(password)
                    )
                    changes = True
                else:
                    return jsonify({"type": "error", "message": "New password must be in 3 to 128 characters!"}), 400
      
            # Update databse only if have changes
            if changes:
                db.session.execute(stmt)
                db.session.commit()

                session["user"] = username
                session["email"] = email

                return jsonify({"type": "success", "message": "All changes have been saved!"}), 200

            return jsonify({"type": "error", "message": "Nothing changed."}), 200
        else:
            # Return always the first error
            return jsonify({"type": "error", "message": list(form.errors.values())[0][0]}), 400


    return render_template("user/index.html", form=form, delForm=deleteForm(), username=session.get("user"), email=session.get("email"))


@app.route("/user/delete", methods=["POST"])
@login_required_api
def delete_account():
    """ Delete user account """

    # Create form object
    form = deleteForm()

    # Validate delete account form
    if form.validate():
        
        # Get form data
        password = form.password.data

        # Get user id and password
        user = db.session.query(User).filter_by(username=session.get("user")).first()

        # Verify if password hashes
        if check_password_hash(user.password, password):

            # Delete all items from user cart
            user_cart = db.session.query(Cart).filter_by(user_id=user.id).all()
            for item in user_cart:
                db.session.delete(item)

            # Delete user
            db.session.delete(user)
            db.session.commit()

            session.clear()

            return jsonify({"type": "success", "message": "Account deleted!"}), 200
        else:
            return jsonify({"type": "error", "message": "Wrong password!"}), 400

    # Return always the first error
    return jsonify({"type": "error", "message": list(form.errors.values())[0][0]}), 400


@app.route("/user/cart", methods=["GET"])
@login_required
def cart():
    """ Show all items in user cart """

    user_id = db.session.query(User.id).filter_by(username=session.get("user"), email=session.get("email")).first()
    products = db.session.query(Cart.product_id).filter_by(user_id=user_id.id).all()

    cart = [db.session.query(Products).filter_by(id=i.product_id).first() for i in products]

    return render_template("cart/index.html", cart=cart)


@app.route("/user/cart/add", methods=["POST"])
@login_required_api
def add_cart():
    """ Add item in user cart """

    data = request.get_json()

    product = db.session.query(Products.id).filter_by(id=data["product_id"]).first()
    user = db.session.query(User.id).filter_by(username=session.get("user"), email=session.get("email")).first()

    if not db.session.query(Cart).filter_by(user_id=user.id, product_id=product.id).first():
        item = Cart(
            user_id=user.id,
            product_id=product.id
        )

        db.session.add(item)
        db.session.commit()

        return jsonify({"type": "success", "message": "Item added to cart!"}), 200

    return jsonify({"type": "error", "message": "Item already in cart!"}), 400


@app.route("/user/cart/remove", methods=["POST"])
@login_required_api
def remove_cart():
    """ Remove item from user cart """

    data = request.get_json()

    product = db.session.query(Products.id).filter_by(id=data["product_id"]).first()
    user = db.session.query(User.id).filter_by(username=session.get("user"), email=session.get("email")).first()
    
    item = db.session.query(Cart).filter_by(user_id=user.id, product_id=product.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()

        return jsonify({"type": "success", "message": "Item removed!"}), 200

    return jsonify({"type": "error", "message": "Item doesn't exist!"}), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login users into application """

    # Create form object
    form = LoginForm()

    if request.method == "POST":
        
        # Validate form
        if form.validate():

            # Get form data
            email = form.email.data
            password = form.password.data

            # Get user data
            user = db.session.query(User).filter_by(email=email).first()

            # Checks user existence and password
            if user is None or not check_password_hash(user.password, password):
                return jsonify({"type": "error", "message": "Wrong email or password!"}), 400

            # Create current user session
            session["user"] = user.username
            session["email"] = user.email

            return jsonify({"type": "success", "message": "Logged!"}), 200
        else:
            # Return always the first error
            return jsonify({"type": "error", "message": list(form.errors.values())[0][0]}), 400

    return render_template("login/index.html", form=form)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """ Create new user account into application """

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
            if db.session.query(User).filter_by(username=username).first():
                return jsonify({"type": "error", "message": "Username already exists!"}), 400

            # Verify if email exists
            if db.session.query(User).filter_by(email=email).first():
                return jsonify({"type": "error", "message": "Email already exists!"}), 400

            # Ensures that passwords are equal
            if password != confirmation:
                return jsonify({"type": "error", "message": "Passwords don't match!"}), 400

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
            
            return jsonify({"type": "success", "message": "Account created!"}), 200
        else:
            # Return always the first error
            return jsonify({"type": "error", "message": list(form.errors.values())[0][0]}), 400

    return render_template("create_account/index.html", form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """ Logout user current session """
    session.clear()
    return redirect(url_for("login"))


if __name__=="__main__":
    app.run(debug=True)

