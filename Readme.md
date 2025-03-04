
### In Short what are the features of TechTales  
<!-- Features -->

1. User can add post with their favourite images 

2. User can also view other's post including admin and other User 

3.  User & Admin Posting – Users can create posts, but only the admin can edit/delete.

4. Anonymous Posting – Posts are visible to all, but authors stay hidden.

5.  Responsive UI – Designed with Bootstrap for a clean look.

6.  Cloud Hosted – Deployed on Render with PostgreSQL.

<!-- Features -->

<!-- What I do in Code in Short -->

### In Short What is in Code 

1.  load config.json put all credential data into that so that our app becomes secure

2.  For Mail we need to get "app password" from google manage account/security and that will be the password "gmail-password"

3.  app.config or app.config.update is use for to set all configuration of flask app (DATABASE,SECRET_KEY,MAIL_SERVER)

4.  app.app_context() is require to create table inside database then we can use db.create_all()

5.  flash messages are important for to print messages , "with messages = get_flashed_messages(with_categories=True)" using these command
    we actually getting all flash messages from flask app

6.  "entry = Contacts(name=name,phone_num=phone, email=email, ,msg=message )" , this are imporatant so that we create row instance

7.  using "db.session.add(entry) " we temporary stores in memory and after using "db.session.commit()" that rows goes to the database permanantly

8.  "mail.send_message(title,sender,recipients=[],body)" this is to send message "recipients are list"

9.  "session" is very imporatant that it stores key value pair in client cookie and require secret_key to generate session because using that key it
    encypts adn decrypts , we can store permanant or temporaray (time-based) sessions

10. "url_for()" is imporatant till i know we can use as 3 diff ways
    - url_for('static',filename='img/css/js') -> to access static file
    - url_for('fn_name' , parameter = p ) -> to access fn inside main.py with parameter if it has
    - url_for('fn_name') -> to access fn inside main.py

11. "redirect()" and "href=''" they append url with current url whether
    url_for('static',filename="img/jpg,css,js") they creates new url link (means doesnt append in url , creates new link)

12. Always use "secure_filename" when user upload files into the server (it's inside werkzeug.utils package)

13. "uuid.uuid4().hex[:32]" maximum 32 bit it creates unique string (it's inside uuid package)

14. "humanize.naturaltime(date1-date2)" usually converts into the human readable format (it's inside humanize package)
    ex: 00-00-00 00:01:32 -> 1 minute ago same as 1 day ago , 1 week ago , 1 year ago

15. We were using "db.context() and then db.create_all()" to create table automatically inside database but problem is
    if we want to add column after this statements then problem occur we again need to drop and then again create so ,
    solution -> "flash-migrate" package - from flask_migrate import Migrate - migrate = Migrate(app,db) -> app is instance of flask and db is instance od database
    then -> i. flask db init -> ii. flask db migrate -m "comment" -> iii. flask upgrade

16. config.json was not uploading to the render because i added this into the ".gitignore" thats why render not able to find

    - what i done is sends "congig.json with data" at runtime and then calls gunicorn then render was able to find config.json
    - echo ' {
      "params":{
      "key":"value
      }
      } ' > config.json && gunicorn main:app -> ("main" is python file and "app" is instance of flask app)

17. I used render Internal cloud database and web service also so that time between backend and database would be fast

18. i used my own logic for pagination and that is always the post request
    - pagination is depends on 'direction' and i sorted as like according to the date in descending means latest will be the first

19. "re" means regex that was important to analyse content and if "** something **" like comes then it replace with 'div' block and creates like a new
    box so that writer or reader might get best experience

20. "psycopg2-binary" important library so that it use for like to connect postgres server whether it's on any server this module is require (explain me
    this in detail )

21. "time_ago_converted" function which is uses "humanize" module to round up the time like ex- 1 day ago , 1 min ago , 1 week ago

22. "app.config['UPLOAD_FILE']" i use to save users images and allowed file is only {'png', 'jpg', 'jpeg', 'gif','webp'} 
    - using "rsplit()" i am checking whether extension is allowed or not if not then it throws error 
    - for checking is filename is normal or not for that i used "secure_filename()" from module "werkzeug.utils"

23. For login is for only "admin" so that admin can remove images , changes title , sub_heading , content of any post or blog
    - For normal user directly can see the blogs but can't change their post i know thats the limitation but i will optimize that  

24. So , Problem is whenever render Server sleeps then whatever the images uploaded by users that get vanished
    - So i used cloud file stoarage to store user images using " DropBox " 
    - DropBox Automatically Saves clients data and it is slow but images are rendering even render servers goes to sleep

<!-- What I do in Code in Short -->