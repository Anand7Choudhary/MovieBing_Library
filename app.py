from flask import Flask,render_template,request
app=Flask(__name__)

app = Flask(
 __name__,
 template_folder="./templates",
 static_folder="./static",
)

@app.route("/json")
def json_response():
    response = {"name": "Pratap", "age": 24}
    #return jasonify
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.errorhandler(404)
def pagenotfound(e):
    return render_template("error404.html")

if __name__=="__main__":
    app.run(debug=True,port=5000,host='0.0.0.0')