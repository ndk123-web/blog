<!-- REQUIREMENTS -->

1.  load config.json put all credential data into that so that our app becomes secure 
2.  For Mail we need to get "app password" from google manage account/security and that will be the password "gmail-password"
3.  app.config or app.config.update is use for to set all configuration of flask app (DATABASE,SECRET_KEY,MAIL_SERVER)
4.  app.app_context() is require to create table inside database then we can use db.create_all()
5.  flash messages are important for to print messages , "with messages = get_flashed_messages(with_categories=True)" using these command
    we actually getting all flash messages from flask app 
6.  "entry = Contacts(name=name,phone_num=phone, email=email, ,msg=message )" , this are imporatant so that we create row instance
7.  using "session.add(entry) " we temporary stores in memory and after using "session.commit()" that rows goes to the database permanantly
8.  "mail.send_message(title,sender,recipients=[],body)" this is to send message "recipients are list"
9.  "session" is very imporatant that it stores key value pair in client cookie and require secret_key to generate session because using that key it 
    encypts adn decrypts , we can store permanant or temporaray (time-based) sessions 
10. "url_for()" is imporatant till i know we can use as 3 diff ways 
    - url_for('static',filename='img/css/js')  -> to access static file
    - url_for('fn_name' , parameter = p )      -> to access fn inside main.py with parameter if it has 
    - url_for('fn_name')                       -> to access fn inside main.py 
11. "redirect()" and "href=''" they append url with current url whether
    url_for('static',filename="img/jpg,css,js") they creates new url link (means doesnt append in url , creates new link)

    
---

### **1. Load `config.json` for Credentials (Security Purpose)**
Flask app ke sensitive data (API keys, passwords, etc.) directly code me likhna **unsafe** hota hai.  
Isliye hum **config.json** file me ye sab rakhte hai aur Flask app me load karte hai:

```python
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]
```

Phir `params['gmail-username']`, `params['gmail-password']` use kar sakte hai.

---

### **2. Gmail App Password (for Mail)**
Normal Google password se direct SMTP nahi chalta.  
Iske liye **Google App Password** generate karna padta hai:

🔹 **Path:** Google Account → Security → App Passwords  
🔹 Yahi password `config.json` me **"gmail-password"** me store karega.

---

### **3. `app.config.update()` for Flask Configuration**
Flask ka `app.config.update()` **application-wide settings** set karne ke liye hota hai, jaise:

```python
app.config.update(
    SECRET_KEY='your_secret_key',
    SQLALCHEMY_DATABASE_URI='sqlite:///database.db',
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-username'],
    MAIL_PASSWORD=params['gmail-password']
)
```

**🔹 Important Configuration:**  
- `SECRET_KEY` → Security ke liye (sessions, flash messages, etc.)
- `SQLALCHEMY_DATABASE_URI` → Database ka connection string
- `MAIL_*` → Flask-Mail settings for SMTP

---

### **4. `app.app_context()` and `db.create_all()`**
Flask database create karne ke liye **application context** chahiye hota hai.  
Agar direct `db.create_all()` likhoge toh error aayega.

**✅ Correct Way:**
```python
with app.app_context():
    db.create_all()
```
**Kyun?**  
- `app.app_context()` Flask ko batata hai ki **abhi hum Flask app ke andar kaam kar rahe hai**.
- `db.create_all()` tables create karega jo `SQLAlchemy` models se defined hai.

---

### **5. Flash Messages (`get_flashed_messages()`)**
Flask me **notifications ya alerts** show karne ke liye `flash()` aur `get_flashed_messages()` ka use hota hai.

🔹 **Backend:**
```python
flash("Your message has been sent successfully!", "success")
```

🔹 **HTML (`contact.html` me use hoga):**
```html
{% with messages = get_flashed_messages(with_categories=True) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

---

### **6. `entry = Contacts(...)` → Database Row Instance**
Jab bhi database me **naya data insert** karna ho, pehle ek **row ka instance** create karna padta hai:

```python
entry = Contacts(name=name, phone_num=phone, email=email, msg=message)
```
Isse ek **database row ka object** banta hai, jo abhi sirf memory me hai.

---

### **7. `session.add(entry)` + `session.commit()`**
- `session.add(entry)` → Data ko memory me rakhta hai (database me save **nahi** hota)
- `session.commit()` → Permanent **database me save** karta hai.

```python
db.session.add(entry)
db.session.commit()
```
Agar `commit()` nahi kiya toh data **store nahi hoga**.

---

### **8. `mail.send_message()` → Email Send Karna**
Flask-Mail ka function hai jo **email bhejne** ke liye use hota hai:

```python
mail.send_message(
    'New message from Contact Form',
    sender=email,
    recipients=[params['gmail-username']],
    body=message + "\n" + phone
)
```

**🔹 Breakdown:**
- `title` → Email ka subject
- `sender` → Jis bande ne mail bheja hai (form me diya gaya `email`)
- `recipients` → Jise mail bhejna hai (Flask app ka email)
- `body` → Mail ka content (`message + phone`)

---

### **✅ Summary**
✔ **config.json** → Security ke liye credentials store karna  
✔ **Google App Password** → Gmail SMTP use karne ke liye  
✔ **app.config.update()** → Flask settings configure karna  
✔ **app.app_context()** → Database create karne ke liye  
✔ **flash messages** → User ko alert messages dikhane ke liye  
✔ **session.add() + session.commit()** → Data insert karne ke liye  
✔ **mail.send_message()** → Flask se email bhejne ke liye  