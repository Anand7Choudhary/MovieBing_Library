from distutils.log import debug
import email
from email.policy import default
import json
from enum import auto, unique
from tabnanny import check
from warnings import catch_warnings
from xml.dom.pulldom import ErrorHandler
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column
import re
from matplotlib.pyplot import table
from Classifier import KNearestNeighbours
from operator import itemgetter
import smtplib

app=Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

# variables
loginStatus = "false"
adminLoggedIn = "false"
error = ""
adminEmail=""
adminPassword=""
userDetails=""




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
    # blocked=db.Column(db.Integer,default=0,nullable=False,unique=False)
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

class AdminDb (db.Model):
    id=db.Column(db.Integer,unique=True,autoincrement=True)
    fullname=db.Column(db.String(100),unique=False,nullable=False)
    email=db.Column(db.String(100),unique=False,nullable=False,primary_key=True)
    password=db.Column(db.String(30))
    gender=db.Column(db.String(20))
    adminAccess=db.Column(db.Integer,unique=False,nullable=False,default=0)
    def __repr__(self):
        # return f"{self.id} - {self.title}"
        return '<Admin %r>' % self.id
    
#end of table creation







@app.route("/addToDataBase",methods=['GET','POST'])
def addElements():
    username=request.form['uname']
    fullname=request.form['fname']
    password=request.form['password']
    # res = fullname != '' and all(chr.isalpha() or chr.isspace() for chr in fullname)
    # check if anything is empty
    if username == '' or fullname == '' or password == '':
        error = "Please fill all the fields"
        return render_template('signup.html',error=error)
    if not re.search("^[a-z,A-Z,\s]+$", fullname):
        return render_template('signup.html',error="Invalid Full Name")
    if (bool(re.search(r"\s", username))):
        return render_template('signup.html',error="Username cannot have spaces")
    if len(password)<8:
        return render_template('signup.html',error="Password must be atleast 8 characters long")
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
        # return render_template("error404.html")
        return render_template('index.html',userDetails=userDetails,contact_success="true",contact_success_message="Message not Sent! Please try again later.",movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="false")
    # return render_template('index.html',contact_success="true",contact_success_message="",movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="false")
    return render_template('index.html',userDetails=userDetails,contact_success="true",contact_success_message="Message Sent Successfully! We will get in touch with you ASAP.",movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="false")



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
            global loginStatus
            loginStatus="true"
            global userDetails
            userDetails=MovieLib.query.filter_by(email=request.form['email']).first()
            return render_template('index.html',userDetails=userDetails,loginStatus=loginStatus,movies=movies,apikey="1cdc3975",showLoading="true")
        else:
            return render_template('login.html',error="Invalid Password")
        # checkUsername=MovieLib.query.filter_by(username=request.form['uname']).first()
    except:
        print("hello4")
        return render_template('error404.html')



@app.route("/logout")
def logoutUser():
    global loginStatus
    loginStatus="false"
    global userDetails
    userDetails=None
    return render_template('index.html',userDetails=userDetails,loginStatus=loginStatus,showLoading="false",movies=movies,apikey="1cdc3975")

@app.route("/addAdmin",methods=['GET','POST'])
def addAdmin():
    fullname=request.form['fullname']
    email=request.form['email']
    password=request.form['password']
    # res = fullname != '' and all(chr.isalpha() or chr.isspace() for chr in fullname)
    if fullname == '' or password == '':
        error = "Please fill all the fields"
        return render_template('addUser.html',error=error)
    if not re.search("^[a-z,A-Z,\s]+$", fullname):
        print("not valid")
        return render_template('adminRegister.html',error="Invalid Full Name")
    if len(password)<8:
        return render_template('adminRegister.html',error="Password must be atleast 8 characters long")
    else:
        try:
            checkEmail=AdminDb.query.filter_by(email=request.form['email']).first()
            if(checkEmail!=None):
                print("valid3")
                return render_template('adminRegister.html',error="Email already exists")
            if request.method=='POST':
                fname=request.form['fullname']
                email=request.form['email']
                password=request.form['password']
                gender=request.form['gender']
                adminDb=AdminDb(fullname=fname,email=email,password=password,gender=gender,adminAccess=0)
                db.session.add(adminDb)
                db.session.commit()  
        except:
            return render_template('error404.html')
    return render_template('admin.html',error="")

# @app.route("/adminLogin",methods=['GET','POST'])
# def adminLogin():
#     try:
#         if(request.method=='POST'):
#             userPresent=AdminDb.query.filter_by(email=request.form['email']).first()
#         if(userPresent==None):
#             return render_template('admin.html',error="User not found")
#         check_email=userPresent.email
#         check_pass=userPresent.password
#         fullname=userPresent.fullname
#         if(check_email==request.form['email'] and check_pass==request.form['password']):
#             global adminLoggedIn
#             adminLoggedIn="true"
#             adminDetails=AdminDb.query.filter_by(email=request.form['email']).first()
#             allUser=MovieLib.query.all()
#             return render_template("adminHome.html",adminLoggedIn=adminLoggedIn,fullname=fullname,allUser=allUser,adminDetails=adminDetails)
#         else:
#             return render_template('admin.html',error="Invalid Password")
#         # checkUsername=MovieLib.query.filter_by(username=request.form['uname']).first()
#     except:
#         return render_template('error404.html')

@app.route("/adminLogin",methods=['GET','POST'])
def adminLogin():
    try:
        global adminEmail,adminPassword
        adminEmail=request.form['email']
        print("al "+adminEmail)
        adminPassword=request.form['password']
        if(request.method=='POST'):
            userPresent=AdminDb.query.filter_by(email=request.form['email']).first()
        if(userPresent==None):
            return render_template('admin.html',error="User not found")
        return redirect("/adminLoginBackend")
    except:
        print("al "+"error")
        return render_template('error404.html')
    
    
@app.route("/adminLoginBackend")
def adminLoginBackend():
    try:
        print("entered")
        global adminEmail,adminPassword
        print("alb "+adminEmail)
        userPresent=AdminDb.query.filter_by(email=adminEmail).first()
        if(userPresent==None):
            print("Why here?")
            return render_template('admin.html',error="User not found")
        if(userPresent.adminAccess==0):
            return render_template('admin.html',error="Admin not authorized")
        else:
            check_email=userPresent.email
            check_pass=userPresent.password
            fullname=userPresent.fullname
            print("alb "+check_email)
            if(check_email==adminEmail and check_pass==adminPassword):
                print("going good")
                global adminLoggedIn
                adminLoggedIn="true"
                # global adminEmail,adminPassword
                adminDetails=AdminDb.query.filter_by(email=adminEmail).first()
                print("working here1")
                allUser=MovieLib.query.all()
                print("working here2")
                # all messages in reverse order
                allMessage=ContactDb.query.order_by(ContactDb.id.desc()).all()
                # allMessage=ContactDb.query.all()
                print("working here3")
                allAdmins=AdminDb.query.all()
                # adminEmail=""
                # adminPassword=""
                return render_template('adminHome.html',allAdmins=allAdmins,allMessages=allMessage,adminLoggedIn=adminLoggedIn,fullname=fullname,allUser=allUser,adminDetails=adminDetails)
            else:
                return render_template('admin.html',error="Invalid Password")
            # checkUsername=MovieLib.query.filter_by(username=request.form['uname']).first()
    except:
        print("alb "+"error")
        return render_template('error404.html')

@app.route("/adminLogout",methods=['GET','POST'])
def logoutAdmin():
    global adminLoggedIn
    adminLoggedIn="false"
    return render_template('admin.html')


# delete user
@app.route('/updateAdminAccess/<int:n>/<email>/<adminemail>/<adminpassword>')
def updateAdminAccess(n,email,adminemail,adminpassword):
    try:
        print("hello"+email)
        admin = AdminDb.query.filter_by(email=email).first()
        if(n==0):
            admin.adminAccess=0
        else:
            admin.adminAccess=1
        db.session.add(admin)
        db.session.commit()
        global adminEmail,adminPassword
        adminEmail=adminemail
        adminPassword=adminpassword
        # return render_template('adminHome.html', allUser=allUser)
        return redirect("/adminLoginBackend")
    except:
        print("error")
        return render_template('error404.html')

@app.route('/delete/<email>/<adminemail>/<adminpassword>')
def delete(email,adminemail,adminpassword):
    try:
        print("hello"+email)
        user = MovieLib.query.filter_by(email=email).first()
        db.session.delete(user)
        db.session.commit()
        global adminEmail,adminPassword
        adminEmail=adminemail
        adminPassword=adminpassword
        # return render_template('adminHome.html', allUser=allUser)
        return redirect("/adminLoginBackend")
    except:
        print("error")
        return render_template('error404.html')
    
@app.route('/deleteUserAccount/<email>',methods=['GET','POST'])
def deleteUserAccount(email):
    try:
        if(request.method=='POST'):
            print("hello"+email)
            user = MovieLib.query.filter_by(email=email).first()
            print("1")
            db.session.delete(user)
            print("2")
            db.session.commit()
            print("3")
            return redirect("/login")
    except:
        print("error")
        return render_template('error404.html')
    
@app.route('/updateUserAccount/<email>',methods=['GET','POST'])
def updateUserAccount(email):
    try:
        if(request.method=='POST'):
            global userDetails
            if(len(request.form['password'])<8):
                return render_template('index.html',userDetails=userDetails,loginStatus=loginStatus,movies=movies,apikey="1cdc3975",showLoading="true",updateError="Password must be atleast 8 characters long")
            elif not re.search("^[a-z,A-Z,\s]+$", request.form['fullName']):
                return render_template('index.html',userDetails=userDetails,loginStatus=loginStatus,movies=movies,apikey="1cdc3975",showLoading="true",updateError="Invalid full name provided")
            else:
                print("hello"+email)
                user = MovieLib.query.filter_by(email=email).first()
                print("xyz")
                print(request.form['fullName'])
                user.password=request.form['password']
                print("here")
                user.fullname=request.form['fullName']
                db.session.add(user)
                db.session.commit()
                print("well")
                userDetails=MovieLib.query.filter_by(email=email).first()
                return render_template('index.html',updateError="",userDetails=userDetails,loginStatus=loginStatus,movies=movies,apikey="1cdc3975",showLoading="true")
                # return render_template('adminHome.html', allUser=allUser)
    except:
        print("error")
        return render_template('error404.html')
# 
# 
# 
# 
# 
# main model engine

with open(r'data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open(r'titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)
    movies = [title[0] for title in movie_titles]
    
def knn(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Distances to most distant movie
    max_dist = sorted(model.distances, key=itemgetter(0))[-1]
    # Print list of 10 recommendations < Change value of k for a different number >
    table = list()
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2]])
    return table

@app.route("/recommendations", methods=["POST"])
def recommendations():
    try:
        searchFor = request.form["searchFor"]
        genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
        movies = [title[0] for title in movie_titles]
        genres = data[movies.index(searchFor)]
        test_point = genres
        table = knn(test_point, 8)
        listMovie=[]
        listLink=[]
        for movie, link in table:
        # Displays movie title with link to imdb
            listMovie.append(movie)
            listLink.append(link)
        movieList='...'.join(listMovie)
        linkList='...'.join(listLink)
        print(movieList)
        # return (movieList=movieList, linkList=linkList,movies=movies,apikey="1cdc3975")
        return render_template("index.html",userDetails=userDetails, movieList=movieList, linkList=linkList,movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="true")
    except Exception as e:
        return render_template("index.html",userDetails=userDetails, error=e,movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="false")


# end of main model engine
#
#
#
#
#

# HTML code links
@app.route("/")
def home():
    return render_template("index.html",userDetails=userDetails,movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="true")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

# @app.route("/searchMovies")
# def searchMovies():
#     return render_template("recommendBody.html",movies=movies,apikey="1cdc3975")

@app.route("/setRecommendScrollFalse")
def setRecommendScrollFalse():
    return render_template("index.html",userDetails=userDetails,recommendScroll="false",movies=movies,apikey="1cdc3975",loginStatus=loginStatus,showLoading="false")

@app.errorhandler(404)
def pagenotfound(e):
    return render_template("error404.html")

# Admin Files
@app.route("/admin")
def admin():
    return render_template("admin.html",error="")

@app.route("/adminRegister")
def adminRegister():
    return render_template("adminRegister.html")

if __name__=="__main__":
    app.run(debug=False,host='0.0.0.0')