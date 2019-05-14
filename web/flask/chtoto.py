from flask import Flask, render_template, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename
from flask import make_response


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['Encoding'] = 'UTF-8'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yandexlyceum_gg'


