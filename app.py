from boto3 import client as client_
from flask import Flask, request, redirect, session, render_template
from os.path import join
from datetime import timedelta
from secret import *
from jsonsql import S3DB
from random import choice
from os import urandom
from time import gmtime, time, strftime

# -- Meta Data --

app = Flask(__name__)
app.secret_key = urandom(200)

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

db = S3DB("live-box/db.json", client, NAME)
db.create_table("user", ["username", "password", "last_online", "userprofile_id"])
db.create_table("userprofile", ["color"])

# -- Backend --

# -- Middleware --

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["userNameI"]
        password = request.form["userPassI"]
        user = db.table("user")
        if len(user.filter(username=username, password=password)) == 1:
            session["username"] = username
            user.get(username=username, password=password).update(last_online="آنلاین")
            return redirect("/")
        else:
            return render_template("login.html", alert=True, var="نام کاربری یا رمز عبور اشتباه وارد شده")
    if "username" in session:
        return redirect("/")
    return render_template("login.html", alert=False)

@app.route("/")
def index():
    if "username" in session:
        return redirect("/users")
    else:
        return redirect("/login")

@app.route('/users')
def users():
    if not "username" in session:
        return redirect("/")
    users = db.table("user").filter()
    users_new = []
    for user in users:
        users_new.append(user.data)
    users = []
    for user in users_new:
        if type(user['last_online']) == str:
            user['last_online'] = 'آنلاین'
        elif type(user['last_online']) == float :
            user['last_online'] = strftime('%Y-%m-%d %H:%M:%S', gmtime(user['last_online']))
        users.append(user)
    return render_template("UsersP.html", username=session["username"], users=users)

@app.route('/leave')
def leave():
    if "username" in session:
        username = session["username"]
        user = db.table("user")
        user = user.get(username=username)
        user.update(last_online=time()+12600)
        session.pop("username")
    return redirect("/")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data_id = db.table("userprofile").create(color=choice(COLORS)).id
        username = request.form["userNameI"]
        password = request.form["userPassI"]
        db.table("user").create(username=username, password=password, last_online=time(), userprofile_id=user_data_id)
        return redirect("/login")
    return render_template("register.html")

if __name__ == "__main__":
    app.run()
