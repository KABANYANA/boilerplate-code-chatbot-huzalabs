from flask import Flask, render_template, request,jsonify
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
import re
import requests
import json
import detectlanguage
from detectlanguage import simple_detect # import the translator
from flask_sqlalchemy import SQLAlchemy
from chat import chatBot
chatBot = chatBot()
import datetime


#import nltk 
#nltk.download('punkt')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycop2://joy:LOBNQ22HRiX26coPE7L1C4Ih5A3NWYDN@dpg-cf2kb782i3mnjcg1f6n0-a/chatdb_oh8x"

db = SQLAlchemy(app)

CORS(app)
class Queries(db.model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000))
    answer = db.Column(db.String(1000))
    language = db.Column(db.String(5))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
with app.app_context():
    db.create_all()  
#from flask import get_response

class translator:
    api_url = "https://translate.googleapis.com/translate_a/single"
    client = "?client=gtx&dt=t"
    dt = "&dt=t"

    #fROM English to Kinyarwanda
    def translate(text : str , target_lang : str, source_lang : str):
        sl = f"&sl={source_lang}"
        tl = f"&tl={target_lang}"
        r = requests.get(translator.api_url+ translator.client + translator.dt + sl + tl + "&q=" + text)
        return json.loads(r.text)[0][0][0]

# use this link to get your api key https://detectlanguage.com/
detectlanguage.configuration.api_key = "13e26484ba8a0a3d865573c4868de0a0"
detectlanguage.configuration.secure = True

def process_question(text : str):
  source_lang = simple_detect(text)
  resp = translator.translate(text=text, target_lang='en', source_lang=source_lang)
  return resp, source_lang
def process_answer(text : str, source_lang):
  resp = translator.translate(text=text, target_lang=source_lang, source_lang='en')
  return resp

# create two routes

def preprocessing(text):
    text = text.lower()
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    html_pattern = re.compile('<.*?>')
    text = url_pattern.sub(r'', text)
    text = html_pattern.sub(r'', text)
    text = re.sub(r"[^\w\d'\s]+", ' ', text)

    return text
Q = []
R = []
def process(QUESTION: str):
    Q.append(QUESTION)
    USER_QUERY, SL = process_question(QUESTION) #Translate the original question into english and store the source lang
    RESPONSE = chatBot.get_response(USER_QUERY) #Asking the chatbot question
    ORIGINAL_RESPONSE = process_answer(RESPONSE, SL)
    R.append(ORIGINAL_RESPONSE)
    return ORIGINAL_RESPONSE


@app.route("/",  methods=["GET"])
def index_get():
    return render_template("index.html")

@app.route("/predict",methods=["POST"])
def predict():
    text = request.get_json().get("message")
    #check if text is valid (I let it for you)
    response = process(text)
    # we jsonify our response
    message = {"answer":response}
    return jsonify(message)

if __name__ =='__main__':
    app.run(debug=True)