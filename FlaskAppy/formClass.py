import os, random, sys
from wtforms import Form,StringField, PasswordField, TextAreaField, validators, BooleanField




# User register form
class RegisterForm(Form):
    '''
    Register User form inherited form wtforms Form class
    '''
    name = StringField('Name', [validators.Length(min=5, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')