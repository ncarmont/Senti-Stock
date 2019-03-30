
import os                       
import json                       
import datetime                       

from flask import Flask, redirect, url_for,render_template,request
from bson import ObjectId
from pymongo import MongoClient

app = Flask(__name__)
# client = MongoClient("mongodb://127.0.0.1:27017") #host uri
# db = client.mymongodb #Select the database
# # mongo = PyMongo(app)

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