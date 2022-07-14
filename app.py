import email
from enum import unique
from warnings import catch_warnings
from xml.dom.pulldom import ErrorHandler
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column
import re
import smtplib

app=Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)





# table creation
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///movieLib.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
class MovieLib (db.Model):
    username=db.Column(db.String(80),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False,primary_key=True)
    password=db.Column(db.String(30))
    fullname=db.Column(db.String(100),unique=False,nullable=False)
    gender=db.Column(db.String(20))
    def __repr__(self):
        # return f"{self.id} - {self.title}"
        return '<User %r>' % self.email

class ContactDb (db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=False,nullable=False)
    content=db.Column(db.String(1000),unique=False,nullable=False)
    def __repr__(self):
        # return f"{self.id} - {self.title}"
        return '<Contact %r>' % self.id
    
#end of table creation







@app.route("/addToDataBase",methods=['GET','POST'])
def addElements():
    username=request.form['uname']
    fullname=request.form['fname']
    # res = fullname != '' and all(chr.isalpha() or chr.isspace() for chr in fullname)
    if not re.search("^[a-zA-Z\s]+$", fullname):
        return render_template('signup.html',error="Invalid Full Name")
    if(username.isspace()):
        return render_template('signup.html',error="Username cannot have spaces")
    try:
        checkEmail=MovieLib.query.filter_by(email=request.form['email']).first()
        checkUsername=MovieLib.query.filter_by(username=request.form['uname']).first()
        if(checkEmail!=None or checkUsername!=None):
            return render_template('signup.html',error="Email or Username already exists")
        if request.method=='POST':
            uname=request.form['uname']
            fname=request.form['fname']
            email=request.form['email']
            password=request.form['password']
            gender=request.form['gender']
            userDb=MovieLib(username=uname,email=email,password=password,fullname=fname,gender=gender)
            db.session.add(userDb)
            db.session.commit()
    except:
        return render_template('error404.html')
    return render_template('login.html')

@app.route("/addContact",methods=['GET','POST'])
def addContactInfo():
    try:
        if request.method=='POST':
            email=request.form['recipient-email']
            content=request.form['message-text']
            contactDb=ContactDb(email=email,content=content)
            db.session.add(contactDb)
            db.session.commit()
    except:
        return render_template('error404.html')
    return render_template('index.html',contact_success="true")



@app.route("/validateUserLogin",methods=['GET','POST'])
def loginUser():
    try:
        if(request.method=='POST'):
            print('heelo2')
            userPresent=MovieLib.query.filter_by(email=request.form['email']).first()
        if(userPresent==None):
            return render_template('login.html',error="User not found")
        print("hello3")
        check_email=userPresent.email
        print(check_email)
        check_pass=userPresent.password
        if(check_email==request.form['email'] and check_pass==request.form['password']):
            return render_template('index.html',loginStatus="true")
        else:
            return render_template('login.html',error="Invalid Password")
        # checkUsername=MovieLib.query.filter_by(username=request.form['uname']).first()
    except:
        return render_template('error404.html')



@app.route("/logout")
def logoutUser():
    return render_template('login.html',loginStatus="false")


# HTML code links
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.errorhandler(404)
def pagenotfound(e):
    return render_template("error404.html")

if __name__=="__main__":
    app.run(debug=True)