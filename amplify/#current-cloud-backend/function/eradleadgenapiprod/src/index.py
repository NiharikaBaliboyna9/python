import awsgi
from flask import Flask, request
from flask_cors import CORS, cross_origin
import csv
import main
import os


app = Flask(__name__,  static_url_path='/static')
CORS(app, support_credentials=True)


def handler(event, context):
    return awsgi.response(app, event, context)

@app.route('/generate', methods=['POST'])
@cross_origin(supports_credentials=True)
def generate():
    csv_file = request.files['file']
    links_from_csv = []
    with open(csv_file, 'r', encoding='unicode_escape') as f:
        reader = csv.DictReader(f)
        for row in reader:
            links_from_csv.append({'domain': row['domain'], 'merchant_name': row['merchant_name']})
    filepath = main.generate_info(links_from_csv)
    serverUrl = os.environ.get("API_URL")
    return {'success' : True, 'filepath': serverUrl + filepath}
    

@app.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    username         = request.form['username']
    password         = request.form['password']
    if(username == 'admin@erad.co' and password == 'erad2023'):
        return {
            "success": True,
            "token": 'abc',
        }
    else: 
        return {
            "success": False,
            "message": 'Credentials not match'
        }
