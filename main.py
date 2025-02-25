from flask import Flask # flask meise Flask class ko import kiya
from flask import render_template # import render_template to render 
from flask_sqlalchemy import SQLAlchemy
from flask import request , jsonify , flash , redirect , url_for
import json 
from flask_mail import Mail

# loads config.json as dictionary object of python for security   
with open('config.json','r') as config_file:
    params = json.load(config_file)['params']

# Flask object create kiya 
app = Flask(__name__) # using this flask knows where is the module is 

# app.config is use for set any configuration related to any work 
app.config.update(
    MAIL_SERVER =  params['gmail-server'],
    MAIL_PORT = params['gmail-port'],
    MAIL_USE_SSL =  params['gmail-ssl'],
    MAIL_USE_TSL = params['gmail-tsl'],
    MAIL_USERNAME = params['gmail-username'],
    MAIL_PASSWORD = params['gmail-password']
)

mail = Mail(app)      # created object of Mail object


# app.config is use for set any configuration related to any work 
app.config['SECRET_KEY'] = params['secret_key']     # required for flash messages , sessions (encryption and descryption)
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']  # require for database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = params['SQLALCHEMY_TRACK_MODIFICATIONS']  # Warning avoid karne ke liye

db = SQLAlchemy(app)  # created object of database clean_blog

# class creation
class Contacts(db.Model):
    sno = db.Column(db.Integer,primary_key=True) 
    name = db.Column(db.String(80),nullable=False) 
    phone_num = db.Column(db.String(120), nullable=False) 
    email = db.Column(db.String(20),unique = False , nullable=False) 
    msg = db.Column(db.String(100),nullable=False)
    date = db.Column(db.String(12)) 

# actually it creates table if doesn't exist
with app.app_context():
    db.create_all()  # only using db.create_all() get error context required 

@app.route('/')
def home():
    return render_template("index.html",params=params)

@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name') 
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        if not name or not email or not phone or not message:
            flash("Please fill all the fields","danger")  # flash to show messages 
            return redirect(url_for('contact'))
        
        entry = Contacts(name=name,          # creates row object instance
                         phone_num=phone,
                         email=email,
                         msg=message
                         )
        
        db.session.add(entry)  # temporary add in the memory
        db.session.commit()    # actual data or row add into the database
        
        # we used gmail password api from app password from manage accounts
        mail.send_message('new message from Blog ' + name,
                          sender=email,
                          recipients=[params['gmail-username']],
                          body = message + '\n' + phone 
                          )
        
        flash("Your message is successfully sends","success")  # flash to show messages
        return redirect('contact')  
        
    return render_template("contact.html",params=params)

@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/post')
def post():
    return render_template('post.html',params=params)

if __name__ == '__main__':
    app.run(debug=True)


# set FLASK_APP=main.py  -> avoid space
# flask run --port=8000 --host=0.0.0.0
# flask --app main.py run --port=8000 --host=0.0.0.0 