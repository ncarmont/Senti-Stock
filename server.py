from flask import Flask, redirect, url_for
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def home():
    return "My flask app"

@app.route("/page",methods=["GET", "POST"])
def func1():
    if request.form:
        # redirect(url_for('page'))
        return render_template("graphs.html", var = request.form)
    return render_template("home.html")
  
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080,debug=True)