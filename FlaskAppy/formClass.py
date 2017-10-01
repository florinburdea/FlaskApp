# --------------------------------------------------------------------------
# Imports
from wtforms import Form, StringField, PasswordField, TextAreaField, validators


#--------------------------------------------------------------------------


#--------------------------------------------------------------------------

# Article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=5, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])


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

class EditForm(Form):
    '''
    Edit Article form that will be used to get data from the DB
    '''
    title = StringField('Title', [validators.Length(min=5, max=50)])
    body = StringField('Body', [validators.Length(min=30)])
