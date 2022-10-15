# flask-wtf for forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired


# Register Form
class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    button = SubmitField("Register")


# Login Form
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    button = SubmitField("Login")


# Search A Movie Form
class SearchMovieForm(FlaskForm):
    movie_name = StringField("Movie Name", validators=[DataRequired()])
    button = SubmitField("Search")


# Cart Form
class CartForm(FlaskForm):
     text = TextAreaField("Text", validators=[DataRequired()])
     button = SubmitField("Submit")


# Comment Form
class CommentForm(FlaskForm):
    text = TextAreaField("Text", validators=[DataRequired()])
    button = SubmitField("Submit")