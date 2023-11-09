import base64
import json
from urllib.parse import quote_plus, urlencode
import requests
from authlib.integrations.flask_client import OAuth
from flask_session import Session
from flask import Flask, abort, redirect, render_template, request, session, url_for,g,make_response




appConf = {
   "OAUTH2_CLIENT_ID": "JRisETWhnuATZgNfI6nAcVW6rPCM0zEgyrApMoMF",
    "OAUTH2_CLIENT_SECRET": "45SupzbbemCPYsCdsnRxZSNDkdtU1aFzz5oikkkyd5mLomXpn5oFUHm4hMLJOVDkC9gEN8DAo5sqiiAc2muKg7njPmV0xJkxNrSXtsIDLVRFoA8Qqwaze3jAWQlDpdOo",
    "OAUTH2_ISSUER": "http://localhost:8000/o/authorize/",
    "FLASK_SECRET": "jhvf89298436bjavfjvef932499346",
    "FLASK_PORT": 8001
}
app = Flask(__name__)

app.secret_key = appConf.get("FLASK_SECRET")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
oauth = OAuth(app)
oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    authorize_url='http://localhost:8000/o/authorize/',
    authorize_params=None,
    authorize_params_provider=None,
    authorize_prompt='consent',
    authorize_response_type='code',
    authorize_params_class=None,
    access_token_url='http://localhost:8000/o/token/',
    
    client_kwargs={
        "scope": "read write",
        'code_challenge_method': 'S256'  
    },
)

@app.route("/")
def home():
    resp = make_response( render_template(
        "home.html",
        session=session,
        pretty=json.dumps(session.get("user"), indent=4),
    ))
    resp.delete_cookie('sessionid')
    #resp.delete_cookie('csrftoken')
    return resp

@app.route("/callback")
def callback(): 
    try:
       token = oauth.myApp.authorize_access_token()
    except:
        return redirect(url_for("loggedOut"))
    session["user"] = token
    session.modified = True
    return redirect(url_for("home"))

@app.route("/login")
def login():
    if "user" in session:
        abort(404)
    redirect_uri=url_for("callback", _external=True)
    session.modified = True
    return oauth.myApp.authorize_redirect(redirect_uri="http://localhost:8001/callback")

@app.route("/loggedout")
def loggedOut():
    session.clear()
    return redirect(url_for("home"))

@app.route('/get_info')
def protected_resource():
    usr = session.get("user")
    access_token = usr["access_token"] 
    headers = {'Authorization': f'Bearer {access_token}'}
    resource_url = 'http://localhost:8000/api/hello/'  
    response = requests.get(resource_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        session["username"] = data["username"]
        session["email"] = data["email"]
        return redirect(url_for("home"))
    else:
        return f'Failed to access protected resource: {response.status_code}'
    

@app.route("/logout")
def logout():
    access_token = session["user"]["access_token"]
    revoke_url = "http://localhost:8000/api/logout/"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(revoke_url, headers=headers)
    if response.status_code==200:
       return redirect("http://localhost:8001/loggedout")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=appConf.get("FLASK_PORT", 3000), debug=True)
