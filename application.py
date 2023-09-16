from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import pandas as pd
# Importing libraries
import numpy as np
import pandas as pd
from scipy.stats import mode
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

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

#column of disease names. We will convert the prognosis column to a numeric
# later on, so this will help us get back to strings
disease_names = df['prognosis']

#turn prognosis column into numeric for logistical regression
encoder = LabelEncoder()
df["prognosis"].replace(encoder.fit_transform(df["prognosis"]),inplace=True)
progs = list(df['prognosis'].unique())
# make into a numeric type
replaceStruct = {
    'prognosis': {}
}
for val in  progs:
  replaceStruct['prognosis'][val] = progs.index(val)
df = df.replace(replaceStruct)

#get x and y for logistical regression
x = df.drop('prognosis',axis='columns')
y=df['prognosis']

# split the data into train and testing
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=.3,random_state=1)

#logistic regression model with an example test case
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
logmodel=LogisticRegression(max_iter=1000,C=1)
logmodel.fit(x_train,y_train)

#example test case
predictions = logmodel.predict(x_test)
final_disease_prediction = disease_names[predictions[0]]


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

