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
    Products().initialize(db.session)


# Setup Flask session
Session(app)


@app.errorhandler(HTTPException)
def error(e):
    """Handles every http execeptions"""
    return render_template("error/error.html", status_code=e.code, error_name=e.name, description=e.description)


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("shop"))


@app.route("/shop", methods=["GET"])
def shop():
    """Get and show all products in database"""

    products = {}
    data = db.session.query(Products).all()

    for i in data:
        products[i.name] = {
            "description": i.description, 
            "price": i.price, 
            "category": i.category, 
            "id": i.id
        }

    return render_template("shop/index.html", products=products)


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

            user = db.session.query(User).filter_by(username=session["user"], email=session["email"]).first()

            # Verify if username exists only if current username is different of session username
            if user.username != username:
                if db.session.query(User).filter_by(username=username).first():
                    return jsonify({"message": "Username already exists!"}), 400
                update = True

            # Verify if email exists only if current email is different of session email
            if user.email != email:
                if db.session.query(User).filter_by(email=email).first():
                    return jsonify({"message": "Email already exists!"}), 400
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


@app.route("/user/cart", methods=["GET"])
def cart():
    """Show all items in user cart"""

    cart = []
    user_id = db.session.query(User.id).filter_by(username=session["user"], email=session["email"]).first()
    products = db.session.query(Cart.product_id).filter_by(user_id=user_id.id).all()

    for i in products:
        cart.append(db.session.query(Products).filter_by(id=i.product_id).first())

    return render_template("cart/index.html", cart=cart)


@app.route("/user/cart/add", methods=["POST"])
def add_cart():
    """Add item in user cart"""

    data = request.get_json()
    product = db.session.query(Products.id).filter_by(id=data["product_id"]).first()

    user_id = db.session.query(User.id).filter_by(username=session["user"], email=session["email"]).first()

    item = Cart(
        user_id=user_id.id,
        product_id=product.id
    )

    db.session.add(item)
    db.session.commit()

    return str(product)


@app.route("/user/cart/remove", methods=["POST"])
def remove_cart():
    """Remove item from user cart"""

    data = request.get_json()
    product = db.session.query(Products.id).filter_by(id=data["product_id"]).first()
    user = db.session.query(User.id).filter_by(username=session["user"], email=session["email"]).first()
    
    item = db.session.query(Cart).filter_by(user_id=user.id, product_id=product.id).first()

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "success"}), 200


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
        user = db.session.query(User).filter_by(username=session["user"]).first()

        # Verify if password hashes
        if check_password_hash(user.password, password):
            db.session.delete(user)
            db.session.commit()

            return jsonify({"message": "success"}), 200
        else:
            return jsonify({"message": "Wrong password!"}), 400

    # Return always the first error
    return jsonify({"message": list(form.errors.values())[0][0]}), 400


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
            user = db.session.query(User).filter_by(email=email).first()

            # Checks user existence and password
            if user is None or not check_password_hash(user.password, password):
                return jsonify({"message": "Wrong email or password!"}), 400

            # Create current user session
            session["user"] = user.username
            session["email"] = user.email

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
            if db.session.query(User).filter_by(username=username).first():
                return jsonify({"message": "Username already exists!"}), 400

            # Verify if email exists
            if db.session.query(User).filter_by(email=email).first():
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


@app.route("/logout", methods=["GET"])
def logout():
    """Logout user current session"""
    session.clear()
    return redirect(url_for("login"))


if __name__=="__main__":
    app.run(debug=True)

