from flask import Flask, render_template, logging, flash, url_for, redirect, session, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from FlaskAppy.formClass import RegisterForm
from FlaskAppy.formClass import ArticleForm
from FlaskAppy.formClass import EditForm


app = Flask(__name__)

#Confi MySql
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='n33pvLkes!'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#Initialize MySql
mysql = MySQL(app)


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
        msg = 'No Articles Foound'
        return render_template('articles.html', msg=msg)

    # Close connenction
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
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
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
    result = cur.execute("SELECT*FROM articles")

    articles = cur.fetchall()

    if result >0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Foound'
        return render_template('dashboard.html', msg=msg)

    # Close connenction
    cur.close()




# Add Article
@app.route('/add_article', methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method =='POST' and form.validate():
        title = form.title.data
        body = form.body.data

        #Create cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES (%s,%s,%s)", (title, body, session['username']))

        #Commit
        mysql.connection.commit()

        #Close connenction
        cur.close()

        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('/add_article.html', form=form)


# Edit Article
@app.route('/edit_article/<string:id>/', methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    form = EditForm(request.form)
    if request.method == 'GET':
        #Create cursor
        cur = mysql.connection.cursor()

        #Execute
        result_title = cur.execute("SELECT title FROM articles WHERE id = %s",[id])
        if result_title > 0:
            # Get stored hash
            data = cur.fetchone()
            title = data['title']
        else:
            title = "Title not received"

        result_body = cur.execute("SELECT body FROM articles WHERE id = %s",[id])
        if result_body > 0:
            # Get stored hash
            data = cur.fetchone()
            body = data['body']
        else:
            body = "Body not received"
        # Close connenction
        cur.close()
        return render_template('edit_article.html', title=title, body=body)
    elif request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("UPDATE articles SET title = %s, body = %s WHERE id = %s",[title,body,id])
        # Commit
        mysql.connection.commit()
        # Close connenction
        cur.close()

        flash('Article changed successfully', 'success')
        return redirect(url_for('dashboard'))

    else:
        flash('Something went wrong!', 'danger')
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.secret_key='hera1234!'
    app.config['SESSION_TYPE'] ='filesystem'
    app.run()
