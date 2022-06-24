from flask import Flask,render_template,request
app=Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.errorhandler(404)
def pagenotfound(e):
    return render_template("error404.html")

if __name__=="__main__":
    app.run(debug=True)