# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired, length

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',  
                         id='username_login',
                         validators=[DataRequired(), length(min=2, max=20)])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired(), length(min=2, max=20)])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired(), length(min=2, max=20)])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired(), length(min=2, max=20)])
