import sqlite3 as sql

from flask import Flask, flash, redirect, render_template, Response, request, session, stream_with_context
from flask_session import Session
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
from tempfile import mkdtemp
# from flask_sqlalchemy import SQLAlchemy

CLIENT_ID = "837769679296-345ubi3bvuj7ke13v6belk9psemnl2r0.apps.googleusercontent.com"

# Start Flask
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Get database connection
def get_db_connection():
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row
    return conn

# Require login on certain pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        status = session.get("status")
        if (status is None) or (not status == "active"):
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    conn = get_db_connection()

    # users = conn.execute("SELECT * FROM users").fetchall()
    # conn.close()

    return render_template("index.html")

@app.route("/callback", methods=["POST"])
def callback():
    # print(request.args["name"])
    # print(request.args["email"])

    # 1) Verify existence and validity of CSRF Cookie 
    csrf_token_cookie = request.cookies.get('g_csrf_token')

    if not csrf_token_cookie:
        return error_page(400, 'No CSRF token in Cookie.')
    csrf_token_body = request.form.get('g_csrf_token')
    if not csrf_token_body:
        return error_page(400, 'No CSRF token in post body.')
    if csrf_token_cookie != csrf_token_body:
        return error_page(400, 'Failed to verify double submit cookie.')

    # 2) Use the verify_oauth2_token to check token validity.
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(request.form.get('credential'), g_requests.Request(),
            CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # 3) ID token is valid. Get the user's Google Account ID from the decoded token.

        session["status"] = "active"
        session["user_id"] = idinfo.get("sub")
        session["user_fname"] = idinfo.get("given_name")
        session["user_lname"] = idinfo.get("family_name")

    except ValueError:
        # 3) If invalid token:
        return error_page(400, 'Invalid token returned.')
        pass
    
    return redirect("/")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def error_page(e, msg):
    return render_template("error.html", code = e, msg = msg)