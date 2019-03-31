
import argparse
import os
                    
import json                       
import datetime      
import six
import sys
import time                 

from flask import Flask, redirect, url_for,render_template,request
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from flask_pymongo import PyMongo
from newsapi import NewsApiClient


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\kshit\\Downloads\\LAHacks2-085ebdbfd067.json"
client = language.LanguageServiceClient()


newsapi = NewsApiClient(api_key='8e9b0daaf3df4a789b34ca0773f9899e')

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mongotest"
mongo = PyMongo(app)

@app.route("/")
def home():
    return "My flask app"

@app.route("/api/savenews",methods=["GET", "POST"])
def savenews():
    if request.form and request.method == 'POST':
        # redirect(url_for('page'))
        print(request.form)
        dict1 = request.form.to_dict()
        company = dict1["company"]
        news_date_from = dict1["newsdate_from"]
        news_date_to = dict1["newsdate_to"]

        if "company_name"  not in mongo.db.list_collection_names():
            mongo.db.createCollection("company_name")

        company_name_collection = mongo.db.company_name

        y,m,d = news_date_from.split('-')
        dateDelt1 = datetime.datetime(int(y),int(m),int(d))

        y,m,d = news_date_to.split('-')
        dateDelt2 = datetime.datetime(int(y),int(m),int(d))
        
        while dateDelt1!=dateDelt2:
            date_string = dateDelt1.strftime('%Y-%m-%d')
            
            if company_name_collection.find_one({"date": date_string}) is None :
                
               
                
                all_articles = request_articles_by_date(company,date_string )
                
                
                json_list = []
                for i in range(0,5):
            
                    article = all_articles['articles'][i]
                    #Insert one article
                    source = article['source']['name']
                    title = article['title']
                    description = article['description']   
                
                    dict_json = {'source': source , 'title' : title , 'description' : description}

                    json_list.append(dict_json)


               

                company_name_collection.insert({'company_name': company, 'date': date_string , 'data': json_list })  
                print("inserted news artciles for a day for one company") 

            else:
                comp = company_name_collection.find_one({"company_name": company})
                print("in else")

            
            dateDelt1 += datetime.timedelta(days=1)

        
        






        return render_template("predict.html", var = dict1)
    return render_template("home.html")





@app.route("/api/savesentiment",methods=["GET", "POST"])
def savesentiment():
    if request.form and request.method == 'POST':
        print(request.form)
        dict1 = request.form.to_dict()
        company = dict1["company"]

        if "company_sentiment"  not in mongo.db.list_collection_names():
            mongo.db.createCollection("company_sentiment")

        company_sentiment_collection = mongo.db.company_sentiment

        company_name_collection = mongo.db.company_name

        cursor = company_name_collection.find({"company_name": company})
        
        for values_of_each_day in cursor:
            sum_val = 0
            counter = 0
            for each_article in values_of_each_day["data"]:
                data = each_article["title"].replace('\n', ' ').lstrip().rstrip()+" " + each_article["description"].lstrip().rstrip() 
                
                
                saliance = analyze_saliance(data,company, client)                 

                if (saliance > 0.05):
                    counter+=1
                    res = analyze_sentiment(data)
                    product = res*saliance
                    sum_val+=product

            average_score_for_day = sum_val/counter

            if company_sentiment_collection.find_one({"date": values_of_each_day["date"]}) is None : 
                company_sentiment_collection.insert({'company_name': company, 'date': values_of_each_day["date"] , 'score': average_score_for_day })
            

            
    
        return render_template("predict.html", var = dict1)

    return render_template("savesentiment.html")






@app.route("/api/plot",methods=["GET", "POST"])
def plot():
    
    return render_template("home.html")

@app.route("/api/textmsg",methods=["GET", "POST"])
def textmsg():
    
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




# RETURNS RELEVANCE OF COMPANY NAME IN ARTICLE
def analyze_saliance(text, keyword_search, client):
    """Detects entity sentiment in the provided text."""
   

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    encoding = enums.EncodingType.UTF32
    if sys.maxunicode == 65535:
        encoding = enums.EncodingType.UTF16

    result = client.analyze_entity_sentiment(document, encoding)
    saliance = 0
    for entity in result.entities:
        
        if (entity.name.lower() == keyword_search.lower()):
            #entity_sent =[entity.name, entity.salience, entity.sentiment]
            saliance =  entity.salience
            break
    return saliance

def analyze_sentiment(content):

  

    # content = 'Your text to analyze, e.g. Hello, world!'

    if isinstance(content, six.binary_type):
        content = content.decode('utf-8')

    type_ = enums.Document.Type.PLAIN_TEXT
    document = {'type': type_, 'content': content}

    response = client.analyze_sentiment(document)
    sentiment = response.document_sentiment
    score = sentiment.score
    magnitude = sentiment.magnitude
    return score*magnitude




def request_articles_by_date(keyword_search,date1):
    all_articles = newsapi.get_everything(q= keyword_search,
                                          #sources='bbc-news,the-verge',
                                          #domains='bbc.co.uk,techcrunch.com',
                                          from_param= date1,
                                          to= date1,
                                          language='en',
                                          sort_by='relevancy',
                                          page_size= 5  )  
    return all_articles










  
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080,debug=True)