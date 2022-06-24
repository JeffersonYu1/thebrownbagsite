import sqlite3 as sql

from flask import Flask, flash, redirect, render_template, Response, request, session, stream_with_context, url_for
from flask_session import Session
from functools import wraps
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
    conn.row_factory = dict_factory
    return conn

# Convert row to dict
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Require login on certain pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        status = session.get("status")
        if (status is None) or (not status == "active"):
            flash("Please log in to continue.", "warning")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    # conn = get_db_connection()
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
            CLIENT_ID, clock_skew_in_seconds=5)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # 3) ID token is valid. Get the user's Google Account ID from the decoded token.
        session["user_id"] = idinfo.get("sub")

    except ValueError as e:
        # 3) If invalid token:
        print(e)
        return error_page(400, 'Invalid token returned.')
        pass

    conn = get_db_connection()
    user_info = conn.execute("SELECT * FROM users WHERE user_id = ?",
        (session.get("user_id"),)).fetchone()
    conn.close()

    if user_info == None:
        session["status"] = "profiling"
        session["idinfo"] = idinfo
        return redirect("/profile")

    else:
        session["status"] = "active"
        session["user_info"] = user_info
    
    return redirect("/")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    # GET
    if request.method == "GET":
        if session.get("status") != "profiling" and session.get("status") != "active":
            flash("Please log in to continue.", "warning")
            return redirect("/")

        if session.get("status") == "profiling":
            if not session.get("idinfo"):
                return error_page(400, 'No ID profile in session.')

            # flash("going to profile page with profiling status", 'success')
            # flash("deez nuts", 'danger')
            user_info = {}
            idinfo = session.get("idinfo")
            user_info["fname"] = idinfo.get("given_name")
            user_info["lname"] = idinfo.get("family_name")
            user_info["email"] = idinfo.get("email")

            print(user_info)
            return render_template("profile.html", user_info = user_info)

        conn = get_db_connection()
        user_info = conn.execute("SELECT * FROM users WHERE user_id = ?",
            (session.get("user_id"),)).fetchone()
        print(user_info)
        conn.close()
        return render_template("profile.html", user_info = user_info)

    # POST
    else:
        form_response = request.form

        print(form_response)

        fname = form_response.get("fname")
        lname = form_response.get("lname")
        pref_f_name = form_response.get("pref_f_name")
        pronouns = form_response.get("pronouns")
        major = form_response.get("major")
        year = form_response.get("year")
        email = form_response.get("email")
        phone = form_response.get("phone")
        instagram = form_response.get("instagram")
        twitter = form_response.get("twitter")
        snapchat = form_response.get("snapchat")

        contact_pref_names = ["SMS", "iMessage", "Email", "GroupMe", "Messenger", "Instagram", "Snapchat", "Twitter"]
        contact_pref_list = []
        for name in contact_pref_names:
            contact_pref_list.append(0 if form_response.get(name + "_check") == None else 1)

        interests = form_response.get("interests")
        
        conn = get_db_connection()
        conn.execute("REPLACE INTO users (user_id, fname, lname, pref_f_name, pronouns, major, year, email, phone, instagram, twitter, snapchat, SMS_check, iMessage_check, Email_check, GroupMe_check, Messenger_check, Instagram_check, Snapchat_check, Twitter_check, interests) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session.get("user_id"), fname, lname, pref_f_name, pronouns, major, year, email, phone,
            instagram, twitter, snapchat, contact_pref_list[0], contact_pref_list[1], contact_pref_list[2],
            contact_pref_list[3], contact_pref_list[4], contact_pref_list[5], contact_pref_list[6], contact_pref_list[7], interests))
        conn.commit()
        user_info = conn.execute("SELECT * FROM users WHERE user_id = ?",
            (session.get("user_id"),)).fetchone()
        conn.close()

        flash("Profile saved.", "info")
        session["status"] = "active"
        print(user_info)
        session["user_info"] = user_info
        return render_template("profile.html", user_info = user_info)

@app.route("/orgstart", methods=["GET", "POST"])
@login_required
def orgstart():
    if request.method == "GET":
        return render_template("orgstart.html")

    else:
        # TODO: POST
        return redirect("/myorgs")

@login_required
@app.route("/myorgs", methods=["GET"])
def myorgs():
    return render_template("myorgs.html")

def error_page(e, msg):
    return render_template("error.html", code = e, msg = msg)


# preferred messaging platforms (inline checkboxes)
# form validation

# new table for bags
# my bags page
# bag creation page
# bag join on home page
# bag join confirmation