from flask import Flask # flask meise Flask class ko import kiya
from flask import render_template # import render_template to render 

# Flask object create kiya 
app = Flask(__name__) # using this flask knows where is the module is 

@app.route("/") 
def home():
    return render_template("index.html")

@app.route("/about") 
def ndk():
    myname = "Navnath"
    return render_template("about.html",name=myname)

# debug = True means automatically reloads 
app.run(debug=True) 

@app.route("/bootstrap") 
def bootstrap():
    return render_template("bootstrap.html")

app.run(debug=True)