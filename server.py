
import os                       
import json                       
import datetime                       

from flask import Flask, redirect, url_for,render_template,request

from flask_pymongo import PyMongo
# from bson import ObjectId
# from pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mongotest"
mongo = PyMongo(app)

@app.route("/")
def home():
    return "My flask app"

@app.route("/page",methods=["GET", "POST"])
def func1():
    if request.form:
        # redirect(url_for('page'))
        print(request.form)
        dict1 = request.form.to_dict()
        company = dict1["company"]
        collec = mongo.db.testcollec
        collec.insert({'company_name':company})
        return render_template("graphs.html", var = request.form)
    return render_template("home.html")

@app.route("/add")
def add(form_data):
    collec = mongo.db.testcollec
    collec.insert({'name':'Apple' , 'cost' : '1000'})
    return("added company")

# @app.route("/user/<companyname>")
# def user_profile(username):
#     user = mongo.db.users.find_one_or_404({"_id": companyname})
#     return render_template("user.html",
#         user=user)
  
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080,debug=True)