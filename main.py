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
import re 
import psycopg
import dropbox

# loads config.json as dictionary object of python for security   
with open('config.json','r') as config_file:
    params = json.load(config_file)['params']

# Flask object create kiya 
app = Flask(__name__) # using this flask knows where is the module is 

DROPBOX_ACCESS_TOKEN = params['DROPBOX_ACCESS_TOKEN']  # Replace with your actual token
DROPBOX_FOLDER_PATH = "/TechTales_Images/"  # Folder inside Dropbox

dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

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
app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_url']  # require for database
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
    title = db.Column(db.String(255), nullable=False) 
    slug = db.Column(db.String(255), nullable=False, unique=True) 
    content = db.Column(db.String(5000), nullable=False)  # Increased content length
    img_url = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Store actual DateTime
    sub_heading = db.Column(db.String(255), nullable=False)  
    is_admin = db.Column(db.String(10), nullable=False)
    
class User(db.Model):
    sno = db.Column(db.Integer,primary_key=True) 
    username = db.Column(db.String(80),nullable=False) 
    password = db.Column(db.String(100), nullable=False) 
    date = db.Column(db.String(12))
    session = db.Column(db.String(256))

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
    per_page = int(params['no_of_posts'])  # Number of posts per page
    page_no = session.get('page_no', 1)  # Default page = 1

    start_idx = (page_no - 1) * per_page
    end_idx = start_idx + per_page
    total_posts = Posts.query.count()  # Get total number of posts

    posts = Posts.query.order_by(Posts.date.desc()).all()[start_idx:end_idx]

    return render_template("index.html", params=params, posts=posts, time_ago_converter=time_ago_converter, page_no=page_no,total_posts=total_posts)


@app.route('/pagination', methods=['POST'])
def pagination():
    per_page = 5  # Number of posts per page
    page_no = session.get('page_no', 1)  # Default page = 1
    total_posts = Posts.query.count()  # Get total number of posts

    # Check which button was clicked
    direction = request.form.get('direction')  

    if direction == "older":
        page_no += 1  # Move forward in pagination
    elif direction == "newer" and page_no > 1:
        page_no -= 1  # Move backward, but not below page 1

    # Update session with new page number
    session['page_no'] = page_no

    # Calculate post range based on current page
    start_idx = (page_no - 1) * per_page
    end_idx = start_idx + per_page
    posts = Posts.query.order_by(Posts.date.desc()).all()[start_idx:end_idx]
    return render_template("index.html", posts=posts, page_no=page_no, params=params, total_posts=total_posts, time_ago_converter=time_ago_converter)   

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
    one_post = Posts.query.filter_by(slug=post_slug).first()  # Fetching the post
    if not one_post:
        return "Post not found", 404  # Return error if post doesn't exist

    # Use regular expression to match any content between ** and **
    processed_content = re.sub(r'\*\*(.*?)\*\*', r'<div class="highlight">\1</div>', one_post.content, flags=re.DOTALL)

    # Pass the processed content to the template
    return render_template('post.html', params=params, one_post=one_post, processed_content=processed_content, time_ago_converter=time_ago_converter)


@app.route('/admin_dashboard/',methods=['GET'])
def admin_dashboard():
    if 'user' in session and session['user'] == params['admin_username']:
        posts = Posts.query.all()
        return render_template('admin_dashboard.html',params=params,posts=posts,time_ago_converter=time_ago_converter)
    return redirect(url_for('login'))

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
    if 'user' in session and session['user'] == params['admin_username']:
        post = Posts.query.filter_by(sno=sno).first()

        if not post:
            flash('Post not found!', 'danger')
            return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            try:
                post.title = request.form.get('title')
                post.sub_heading = request.form.get('sub_heading')
                post.content = request.form.get('content')

                # Preserve old image by default
                img_url = post.img_url  

                # Check if a new image is uploaded
                if 'img_url' in request.files and request.files['img_url'].filename != '':
                    file = request.files['img_url']

                    if file and allowed_file(file.filename):
                        new_img_url = upload_to_dropbox(file)
                        
                        if new_img_url:
                            img_url = new_img_url  # Use new image if upload succeeds
                        else:
                            flash("Failed to upload image. Retaining the old image.", "warning")
                    
                post.img_url = img_url  # Keep the correct image

                db.session.commit()
                flash('Successfully updated the post', 'success')
                return redirect(url_for('home'))  # Redirect after update

            except Exception as e:
                db.session.rollback()
                flash(f'Some error occurred: {str(e)}', 'danger')

        return render_template('edit.html', params=params, post=post)

    return redirect(url_for('login'))


''' < ------------- MOST IMPORTANT ------------------> '''


@app.route('/login/',methods=['GET','POST'])
def login():
    
    posts = Posts.query.all()
    
    # when if 'user' ke is already in cookie then it will immediately redirects to the home 
    if 'user' in session and session['user'] == params['admin_username']:        
            return render_template('admin_dashboard.html',params=params,posts=posts,time_ago_converter=time_ago_converter)   
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == params['admin_username'] and password == params['admin_password']:
            session['user'] = username
            return render_template('admin_dashboard.html',params=params,posts=posts,time_ago_converter=time_ago_converter)        
        else:
            flash('U are not admin','danger')
            return redirect(url_for('login'))
    
    return render_template('login.html',params=params)  

@app.route('/logout/')
def logout():
    session.pop('user')
    return redirect(url_for('login'))

def upload_to_dropbox(file):
    
    # secure the filename means it removes harmful names like '/'
    filename = secure_filename(file.filename)
    
    # it sets dropbox path where the actual image will be going to send 
    dropbox_path = f"{DROPBOX_FOLDER_PATH}{filename}"
    
    try:
        # Upload file.read() sending bytes and that will store in dropbox_path
        # if image already exist then it overwrites instead of error 
        dbx.files_upload(file.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        
        # returns list of sharing list for that path of image
        shared_links = dbx.sharing_list_shared_links(path=dropbox_path).links
        
        # if for that image link is already exist then that link we will be going to use 
        if shared_links:
            link = shared_links[0].url  # Use existing link
            
        # if not exist then we are creating new link for that image
        else:
            link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            link = link_metadata.url
        
        # dropbox.com donot give direct image link because of dl=0 
        # we need to replace dropbox with dl.dropboxusercontent to get direct image link 
        # and that link we are going to store inside the img_url database 
        direct_link = link.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
        return direct_link

    except dropbox.exceptions.ApiError as e:
        print(f"Dropbox API error: {e}")
        return None

@app.route('/createpost/', methods=['GET', 'POST'])
def createpost():
    if request.method == 'POST':
        try:
            title = request.form.get('title')  
            sub_heading = request.form.get('sub_heading')
            content = request.form.get('content')
            date_input = request.form.get('date')
            
            date = datetime.strptime(date_input, '%Y-%m-%d') if date_input else datetime.now()
            slug = title[0:5] + uuid.uuid4().hex[:15]  # Unique slug
            
            is_admin = 'True' if 'user' in session and session['user'] == params['admin_username'] else 'False'
            
            # if user do not uploaded the image then image will be default 
            if 'img_url' not in request.files or request.files['img_url'].filename == '':
                flash('Image not sent. Using default image.', 'warning')
                img_url = "/static/assets/img/about-bg.jpg"  # Default image
            
            # if user selects the image then that image will be process by function upload_to_dropbox  
            else:
                file = request.files['img_url']
                img_url = upload_to_dropbox(file)  # Upload & get URL
                
                if not img_url:
                    flash("Failed to upload image. Using default.", "danger")
                    img_url = "/static/assets/img/about-bg.jpg"

            # 🔹 Save to Database
            entry = Posts(title=title, sub_heading=sub_heading, content=content, date=date, img_url=img_url, slug=slug, is_admin=is_admin)
            db.session.add(entry)
            db.session.commit()
            
            flash('Post successfully created!', 'success')
            return redirect(url_for('home'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Something went wrong: {str(e)}', 'danger')
            return redirect(request.url)
        
    return render_template('create_post.html', post={}, params=params)

@app.route('/delete/<string:sno>')
def delete(sno):
    
    if 'user' in session and session['user'] == params['admin_username']:
        req_post = Posts.query.filter_by(sno=sno).first()
        
        if not req_post:
            flash('Post not found','danger')
            return redirect(url_for('admin_dashboard'))
        
        try:
            db.session.delete(req_post)
            db.session.commit()
            flash('successfully deleted post! ','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Something messing: {e}','danger')
            return redirect(url_for('admin_dashboard'))

        all_posts = Posts.query.filter_by().all()
        return render_template('admin_dashboard.html',params=params,posts=all_posts,time_ago_converter=time_ago_converter)
    else:
        return redirect(url_for('login'))

# @app.route('/pagination/<int:page>/', methods=['GET'])
# def pagination(page):
#     per_page = int(params['no_of_posts'])  # Number of posts per page (default = 5)
    
#     total_posts = Posts.query.count()  # Total number of posts
#     start_index = (page - 1) * per_page
#     end_index = start_index + per_page

#     # Fetch only the required posts
#     posts = Posts.query.order_by(Posts.date.desc()).all()[start_index:end_index]

    # return render_template("index.html", params=params, posts=posts, page=page, total_posts=total_posts, per_page=per_page)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This will create tables if they don't exist
    app.run(debug=True)



# set FLASK_APP=main.py  -> avoid space
# flask run --port=8000 --host=0.0.0.0
# flask --app main.py run --port=8000 --host=0.0.0.0 