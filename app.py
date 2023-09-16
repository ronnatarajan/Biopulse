# Importing libraries
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import numpy as np
import pandas as pd
from scipy.stats import mode
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import sqlite3
from sqlite3 import Error
import os
from werkzeug.security import check_password_hash, generate_password_hash


# Create sql database
db = os.path.realpath('Users.db')

# Connect to sql data
conn = None
try:
    conn = sqlite3.connect(db, check_same_thread=False)
except Error as e:
    print(e)

with open('schema.sql') as f:
    conn.executescript(f.read())

cur = conn.cursor()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Get dataset 
df = pd.read_csv("Dataset/Training.csv")

# Column of disease names. We will convert the prognosis column to a numeric
# Later on, so this will help us get back to strings
disease_names = df['prognosis']
df.drop("Unnamed: 133", axis='columns',inplace=True)

# Turn prognosis column into numeric for logistical regression
encoder = LabelEncoder()
df["prognosis"].replace(encoder.fit_transform(df["prognosis"]),inplace=True)
progs = list(df['prognosis'].unique())
# Make into a numeric type
replaceStruct = {
    'prognosis': {}
}
for val in  progs:
  replaceStruct['prognosis'][val] = progs.index(val)
df = df.replace(replaceStruct)



# Get x and y for logistical regression
x = df.drop('prognosis',axis='columns')
y=df['prognosis']


# Split the data into train and testing
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=.3,random_state=1)

# Logistic regression model with an example test case
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
logmodel=LogisticRegression(max_iter=1000,C=1)
logmodel.fit(x_train,y_train)



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", error = "")
    elif request.method == "POST":
        #user is trying to register
        if request.form.get('log_email')== None:
            #error checking
            if request.form.get("sign_email") == "" or  request.form.get("sign_password") == "":
                return render_template("index.html", error="Please input valid email and password")
            rows = cur.execute("SELECT * FROM users WHERE email = ?;", (request.form.get("sign_email"),)).fetchall()
            #more error checking
            if len(rows) >=1:
                return render_template("index.html", error="There is already an account with the given username")
            #insert user information into database
            if request.form.get("sign_confirm") == request.form.get("sign_password") and not request.form.get("sign_password") == "" and not request.form.get("sign_email") == "":
                print(request.form.get("sign_password"))
                cur.execute("INSERT INTO users (email, hash) VALUES (?,?);", (request.form.get("sign_email"), generate_password_hash(request.form.get("sign_password"))))
                conn.commit()
                return render_template("checklist.html", symptom_list = x.columns)
            else:
                return render_template("index.html", error="Passwords don't match")
            
        elif request.form.get('sign_email')== None:
            """Log user in"""

            print(request.form.get("log_email") == "")

            # Forget any user_id
            session.clear()

            # User reached route via POST (as by submitting a form via POST)
            if request.method == "POST":

                # Ensure username was submitted
                if request.form.get("log_email") == "" or request.form.get("log_password") == "":
                    return render_template("index.html", error="Must enter email and password when logging in")

                # Query database for username
                rows = cur.execute("SELECT * FROM users WHERE email = ?", (request.form.get("log_email"),)).fetchall()
                # Ensure username exists and password is correct
                if len(rows) != 1 or not check_password_hash(rows[0][1], request.form.get("log_password")):
                    return render_template("index.html", error="Incorrect login information")
                print(rows[0][1])
                # Remember which user has logged in
                session["user_email"] = rows[0][0]
                session["user_password"] = rows[0][1]


                # Redirect user to home page
                return render_template("checklist.html", symptom_list = x.columns)


        # if request.form.get()
        # #error checking
        # if not request.form.get("username") or not request.form.get("password"):
        #     return render_template("index.html", error = "Missing Username or Password")
        # rows = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))
        # #more error checking
        # if len(rows) >=1:
        #     return render_template("index.html", error = "Username is taken")
        # #insert user information into database
        # if request.form.get("password") == request.form.get("confirmation") and request.form.get("username") and request.form.get("password"):
        #     db.execute("INSERT INTO users (username, hash) VALUES (?,?);", request.form.get("username"), generate_password_hash(request.form.get("password")))
        #     return render_template("login.html")
        # else:
        #     return apology("Passwords do not match")
        return render_template("index.html", error = "")

    return render_template("index.html", error = "")
