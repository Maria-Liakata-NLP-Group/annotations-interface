from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    user = {"email": "random.user@random.com"}
    return render_template('index.html', user=user)
