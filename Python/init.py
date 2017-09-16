#Init Python file
#Located in the core source

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
@app.route('/<user>')
def index(user=None):
	return render_template('user.html', user = user)

@app.route('/shoping')
def shoping():
    food = ["Cheese","Tuna","Salad" ]
    return render_template("shoping.html", food = food )

if __name__=="__main__":
	app.run()

