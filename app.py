from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging 
import pymongo
logging.basicConfig(level = logging.INFO, filename = 'scrappers.log', filemode = 'w', format = '%(asctime)s - %(levelname)s - %(message)s')
import os

app=Flask(__name__)

@app.route("/",methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review",methods=['POST','GET'])
def index():
    if(request.method=='POST'):
        try:
            query = request.form['content'].replace(" ","")
            save_dir = 'images/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"} 
            response = requests.get(f"https://in.images.search.yahoo.com/search/images;_ylt=Awrx_xY7Bhdlt54YDQC7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?p={query}&fr2=piv-web&type=E211IN714G0&fr=mcafee")
            soup = bs(response.content,"html.parser")
            image_tags = soup.find_all("img")
            del image_tags[0]
            image_data_list = []
            for i in image_tags:
                if i.name=='img' and 'src' in i.attrs:
                    image_url = i['src']
                    image_data = requests.get(image_url).content 
                    mydict = {"index":image_url,"image":image_data}
                    image_data_list.append(mydict) 
                    with open(os.path.join(save_dir,f"{query}_{image_tags.index(i)}.jpg"),"wb") as f:
                           f.write(image_data)
            
            client = pymongo.MongoClient("mongodb+srv://sonwaneshivani:shivani6@cluster0.6ic1qsr.mongodb.net/?retryWrites=true&w=majority")
            db=client['img_db'] 
            coll=db['img_coll'] 
            coll.insert_many(image_data_list)

            return render_template('result.html', image_data_list=image_data_list)
        except Exception as e:
            logging.info(e)
            logging.shutdown()
            return "something is wrong"
    else:
        return render_template('index.html')  

if __name__=="__main__":
    app.run(host='0.0.0.0')           

