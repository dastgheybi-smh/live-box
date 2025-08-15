from boto3 import client as client_
from flask import Flask, request, redirect, session
from os.path import join
from pytml import render
from datetime import timedelta
from secret import *

# -- Meta Data --

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=5)

client = client_(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_TOKEN,
    aws_secret_access_key=SECRET
)

COLORS = [
    "#908F49",
    "#8A221F",
    "#6C2364",
    "#1A1B61",
    "#206861",
    "#1F6817"
]

BASE_DIR = "C:\\ProgramData\\Live code"
TEMP_DIR = join(BASE_DIR, "temp")

# -- Database Settings --
#todo: make db

# -- Backend --

# -- Middleware --

@app.route("/login", methods=["GET", "POST"])
def login():
    return render("templates/login.html")

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" in session:
        return "You are logged in"
    else:
        return redirect("/login")

@app.route('/register')
def register():
    return render("templates/register.html")

if __name__ == "__main__":
    app.run()
