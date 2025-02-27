from flask import Flask # flask meise Flask class ko import kiya
from flask import render_template # import render_template to render 
from flask_sqlalchemy import SQLAlchemy
from flask import request , jsonify , flash , redirect , url_for , session
import json , os
from datetime import datetime
from flask_mail import Mail
from werkzeug.utils import secure_filename
import uuid
from flask_migrate import Migrate
import humanize

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

migrate = Migrate(app,db)

# class creation
class Contacts(db.Model):
    sno = db.Column(db.Integer,primary_key=True) 
    name = db.Column(db.String(80),nullable=False) 
    phone_num = db.Column(db.String(120), nullable=False) 
    email = db.Column(db.String(20),unique = False , nullable=False) 
    msg = db.Column(db.String   (100),nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)  

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(80), nullable=False) 
    slug = db.Column(db.String(21), nullable=False, unique=True) 
    content = db.Column(db.String(5000), nullable=False)  # Increased content length
    img_url = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Store actual DateTime
    sub_heading = db.Column(db.String(50), nullable=False)  
    is_admin = db.Column(db.String(10), nullable=False)
    
# class User(db.Model):
#     sno = db.Column(db.Integer,primary_key=True) 
#     username = db.Column(db.String(80),nullable=False) 
#     password = db.Column(db.String(100), nullable=False) 
#     date = db.Column(db.String(12))
#     session = db.Column(db.String(256))

# actually it creates table if doesn't exist
# only using db.create_all() get error context required 
    # with app.app_context(): 
    #     db.create_all()  
# only using this we can create above all tables and if not then creates if exist then column must match

''' ----------- IMP FOR TIME CONVERSION ----------------- '''
def time_ago_converter(date_obj):
    if isinstance(date_obj, str):  # If date is stored as a string (which it shouldn't be)
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')  # Convert to datetime
    
    now = datetime.now()

    if date_obj > now:  # Future date handling
        return humanize.naturaltime(date_obj - now)  # "In X days"
    
    return humanize.naturaltime(now - date_obj)  # "X time ago"
''' ----------- IMP FOR TIME CONVERSION ----------------- '''

@app.route('/')
def home():
    posts = Posts.query.order_by(Posts.date.desc()).all()[0:int(params['no_of_posts'])]  # Fetch all
    return render_template("index.html", params=params, posts=posts, time_ago_converter=time_ago_converter)

@app.route('/contact/',methods=['GET','POST'])
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
        
    return render_template("contact.html",params=params,one_post={})

@app.route('/about/')
def about():
    return render_template('about.html',params=params,one_post={})

@app.route('/post/')
def normal_post():
    return render_template('post.html',params=params,one_post={})


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    one_post = Posts.query.filter_by(slug=post_slug).first()  # ✅ Single post fetch kar rahe hai
    if not one_post:
        return "Post not found", 404  # ✅ Agar post nahi mili to error return kare
    return render_template('post.html', params=params, one_post=one_post, time_ago_converter=time_ago_converter)  # ✅ Correct variable pass ho raha hai

@app.route('/admin_dashboard/',methods=['GET'])
def admin_dashboard():
    posts = Posts.query.all()
    return render_template('admin_dashboard.html',params=params,posts=posts)

''' ------------ Imp for uploading file --------------- '''

UPLOAD_FOLDER = os.path.join(app.root_path, 'static/assets/img/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

''' ------------ Imp for uploading file --------------- '''

''' < ------------- MOST IMPORTANT ------------------> '''

@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session:
        post = Posts.query.filter_by(sno=sno).first()
        
        if not post:
            flash('Post not found!', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        if request.method == 'POST':
            try:
                post.title = request.form.get('title')
                post.sub_heading = request.form.get('sub_heading')
                post.content = request.form.get('content')

                # Check if a new image is uploaded
                if 'img_url' in request.files and request.files['img_url'].filename != '':
                    file = request.files['img_url']

                    if file and allowed_file(file.filename):
                        if not os.path.exists(app.config['UPLOAD_FOLDER']):
                            os.makedirs(app.config['UPLOAD_FOLDER'])

                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        post.img_url = filename  # Update image filename in DB

                db.session.commit()
                flash('Successfully updated the post', 'success')
                return redirect(url_for('home'))  # Reload page after update
            
            except Exception as e:
                db.session.rollback()
                flash(f'Some error occurred: {str(e)}', 'danger')
        
        return render_template('edit.html', params=params, post=post)
    
    return render_template('login.html')

''' < ------------- MOST IMPORTANT ------------------> '''


@app.route('/login/',methods=['GET','POST'])
def login():
    
    posts = Posts.query.all()
    
    # when if 'user' ke is already in cookie then it will immediately redirects to the home 
    if 'user' in session and session['user'] == params['admin_username']:        
        return render_template('admin_dashboard.html',params=params,posts=posts)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == params['admin_username'] and password == params['admin_password']:
            session['user'] = username
            return render_template('admin_dashboard.html',params=params,posts=posts)        
        else:
            flash('U are not admin','danger')
            return redirect(url_for('login'))
    
    return render_template('login.html',params=params)

@app.route('/logout/')
def logout():
    session.pop('user')
    return redirect(url_for('login'))

@app.route('/createpost/',methods=['GET','POST'])
def createpost():
    if request.method == 'POST':
        try:
            title = request.form.get('title')  
            sub_heading = request.form.get('sub_heading')
            content = request.form.get('content')
            date_input = request.form.get('date')
            
            # Date handling
            date = datetime.strptime(date_input, '%Y-%m-%d') if date_input else datetime.now()
            slug = title + uuid.uuid4().hex[:32] # generates unique ID (first 8 chars)
            
            if 'user' in session and session['user'] == params['admin_username']: # if admin 
                is_admin = 'True'
            else:
                is_admin = 'False'
            
            # File Handling
            if 'img_url' not in request.files:
                flash('Image not sent', 'danger')
                return redirect(request.url)

            file = request.files['img_url']
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = app.config['UPLOAD_FOLDER']
                
                # Ensure upload folder exists
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                filepath = os.path.join(upload_path, filename)
                file.save(filepath)
            else:
                flash("Invalid file format. Using default image.", "danger")
                filename = "about-bg.jpg"
                filepath = os.path.join(os.getcwd(),"static", "assets", "img", filename)
            
            # Save to database
            entry = Posts(title=title, sub_heading=sub_heading, content=content, date=date, img_url=filename ,slug = slug ,is_admin=is_admin)
            db.session.add(entry)
            db.session.commit()
            flash('Successfully created', 'success')
            return redirect(url_for('home'))  # Redirect to home or blog list page
            
        except Exception as e:
            db.session.rollback()
            flash(f'Something went wrong: {str(e)}', 'danger')
            return redirect(request.url)
        
    return render_template('create_post.html', post={},params = params)


if __name__ == '__main__':
    app.run(debug=True)


# set FLASK_APP=main.py  -> avoid space
# flask run --port=8000 --host=0.0.0.0
# flask --app main.py run --port=8000 --host=0.0.0.0 