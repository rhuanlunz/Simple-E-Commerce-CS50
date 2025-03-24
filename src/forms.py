from wtforms                import EmailField, StringField, PasswordField, SubmitField
from wtforms.validators     import InputRequired, Length, Email
from flask_wtf              import FlaskForm


MIN             = 4
MAX_USER        = 30
MAX_PASS        = 128
MAX_EMAIL       = 254
CLASS_INPUT     = "form-control rounded-5 mb-2"
CLASS_BTN       = "btn btn-primary fw-bold p-2 rounded-5 w-100"
CLASS_DEL_BTN   = "btn btn-danger p-2 rounded-5 flex-grow-1 ms-1"


class LoginForm(FlaskForm): 
    email = EmailField(
        "Email", 
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Email"
        },
        validators=[
            InputRequired("Email required!"), 
            Email("Invalid email!"),
            Length(min=MIN, max=MAX_EMAIL, message=f"Email must be in {MIN} to {MAX_EMAIL} characters")
        ]
    )

    password = PasswordField(
        "Password",
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Password"
        },
        validators=[
            InputRequired("Password required"),
            Length(min=MIN, max=MAX_PASS, message=f"Password must be in {MIN} to {MAX_PASS} characters")
        ]
    )

    submit = SubmitField(
        "Sign in",
        render_kw={
            "class": CLASS_BTN
        }
    )


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", 
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Username"
        },
        validators=[
            InputRequired("Username required!"), 
            Length(min=MIN, max=MAX_USER, message=f"Username must be in {MIN} to {MAX_USER} characters")
        ]
    )

    email = EmailField(
        "Email", 
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Email"
        },
        validators=[
            InputRequired("Email required!"), 
            Email("Invalid email!"),
            Length(min=MIN, max=MAX_EMAIL, message=f"Email must be in {MIN} to {MAX_EMAIL} characters")
        ]
    )

    password = PasswordField(
        "Password",
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Password"
        },
        validators=[
            InputRequired("Password required"),
            Length(min=MIN, max=MAX_PASS, message=f"Password must be in {MIN} to {MAX_PASS} characters")
        ]
    )

    confirmation = PasswordField(
        "Password confirmation",
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Password confirmation"
        },
        validators=[
            InputRequired("Password confirmation required"),
            Length(min=MIN, max=MAX_PASS, message=f"Password confirmation must be in {MIN} to {MAX_PASS} characters")
        ]
    ) 

    submit = SubmitField(
        "Create account",
        render_kw={
            "class": CLASS_BTN
        },
    )


class editForm(FlaskForm):
    username = StringField(
        "Username", 
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Username"
        },
        validators=[
            InputRequired("Username required!"), 
            Length(min=MIN, max=MAX_USER, message=f"Username must be in {MIN} to {MAX_USER} characters")
        ]
    )

    email = EmailField(
        "Email", 
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Email"
        },
        validators=[
            InputRequired("Email required!"), 
            Email("Invalid email!"),
            Length(min=MIN, max=MAX_EMAIL, message=f"Email must be in {MIN} to {MAX_EMAIL} characters")
        ]
    )

    password = PasswordField(
        "New password",
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "New Password"
        },
    )
  
    submit = SubmitField(
        "Save changes",
        render_kw={
            "class": CLASS_BTN
        },
    )

class deleteForm(FlaskForm):
    password = PasswordField(
        "Password",
        render_kw={
            "class": CLASS_INPUT,
            "placeholder": "Confirm your password"
        },
        validators=[
            InputRequired("Password required"),
            Length(min=MIN, max=MAX_PASS, message=f"Password must be in {MIN} to {MAX_PASS} characters")
        ]
    )
  
    submit = SubmitField(
        "Delete",
        render_kw={
            "class": CLASS_DEL_BTN
        },
    )
