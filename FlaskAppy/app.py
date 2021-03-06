from functools import wraps
from flask import Flask, render_template, flash, url_for, redirect, session, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask.ext.mail import Mail, Message
import os

from formClass import ArticleForm
from formClass import EditForm
from formClass import RegisterForm

app = Flask(__name__)

# Config MySql
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='dt2017'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

# Config Email
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Config Email Message
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[MyFlaskApp]'
app.config['FLASKY_MAIL_SENDER'] = 'MyFlaskApp Admin <florinburdea@gmail.com>'


# Initialize MySql
mysql = MySQL(app)

# Initialize Mail
mail = Mail(app)

# Home page
@app.route('/')
def index():
    return render_template('home.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

#Article page
@app.route('/articles')
def articles():
    #Create cursor
    cur = mysql.connection.cursor()

    #Get articles
    result = cur.execute("SELECT*FROM articles")

    articles = cur.fetchall()

    if result >0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)

    # Close connection
    cur.close()


@app.route('/article/<string:id>/')
def article(id):
    #Create cursor
    cur = mysql.connection.cursor()

    #Get article
    cur.execute("SELECT*FROM articles WHERE id = %s",[id])

    article = cur.fetchone()
    return render_template('article.html', article=article)


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method =='POST' and form.validate():
        session['name'] = form.name.data
        session['email'] = form.email.data
        session['username'] = form.username.data
        session['password'] = sha256_crypt.encrypt(str(form.password.data))

        #Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (session['name'], 
                                                                                                   session['email'], 
                                                                                                   session['username'], 
                                                                                                   session['password']))
        #Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('You are now registered and can log in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html',form=form)


# User login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Get Form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by name from DB
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # Login successful
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = "Invalid login."
                return render_template('login.html', error=error)
            # Close DB connection
            cur.close()

        else:
            error = "Username not found. Pleae try again."
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:

            return f(*args, **kwargs)
        else:
            flash('Unauthorised. Please login.', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout routing
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

# User dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    #Create cursor
    cur = mysql.connection.cursor()

    #Get articles
    result = cur.execute("SELECT*FROM articles WHERE author = %s", [session['username']])

    articles = cur.fetchall()

    if result >0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)

    # Close connection
    cur.close()




# Add Article
@app.route('/add_article', methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method =='POST' and form.validate():
        session['title'] = form.title.data
        session['body'] = form.body.data

        #Create cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES (%s,%s,%s)", (session['title'], 
                                                                                    session['body'], 
                                                                                    session['username']))

        #Commit
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('/add_article.html', form=form)


# Edit Article
#TODO add the edit bar to the edit_article.htlm page as on add_article.html
@app.route('/edit_article/<string:id>/', methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    form = EditForm(request.form)
    if request.method == 'GET':

        #Create cursor
        cur = mysql.connection.cursor()

        #Execute
        result_title = cur.execute("SELECT title, body FROM articles WHERE id = %s",[id])
        if result_title > 0:

            # Get stored hash
            data = cur.fetchone()
            title = data['title']
            body = data['body']
        else:
            title, body = "Title or body not found."

        # Close connection
        cur.close()

        return render_template('edit_article.html', title=title, body=body, form=form)

    elif request.method == 'POST' and form.validate():
        session['title'] = form.title.data
        session['body'] = form.body.data

        # Create cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("UPDATE articles SET title = %s, body = %s WHERE id = %s",[session['title'],session['body'],id])
        # Commit
        mysql.connection.commit()
        # Close connection
        cur.close()

        flash('Article changed successfully', 'success')
        return redirect(url_for('dashboard'))

    else:
        flash('Something went wrong!', 'danger')
    return redirect(url_for('dashboard'))


# Delete Article
@app.route('/del_article/<string:id>/')
@is_logged_in
def del_article(id):

    #Create cursor
    cur = mysql.connection.cursor()
    #Execute
    cur.execute("DELETE FROM articles WHERE id = %s",[id])
    # Commit
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('Article deleted', 'success')
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.secret_key='hera1234!'
    app.config['SESSION_TYPE'] ='filesystem'
    app.run()
