from flask import Flask,render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import math

with open('config.json','r') as c:
    params = json.load(c)['params']

local_sercer = True

app = Flask(__name__)
app.secret_key = "super secret key"
app.config.update(MAIL_SERVER = 'smtp.gmail.com', 
MAIL_PORT = '465', 
MAIL_USE_SSL = True,
MAIL_USERNAME = params['gmail_user'], 
MAIL_PASSWORD = params['gmail_password']
)
mail = Mail(app)

if local_sercer:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    """ sno , name , email , phone_num , msg , date"""
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    """ sno , name , email , phone_num , msg , date"""
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(130), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_name = db.Column(db.String(12), nullable=True)

class Tut(db.Model):
    """ sno , name , email , phone_num , msg , date"""
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tut_slug = db.Column(db.String(12), nullable=True)
    tagline = db.Column(db.String(21), nullable=False)
    img_name = db.Column(db.String(12), nullable=True)
    date = db.Column(db.String(12), nullable=True)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / params['no_of_posts'])

    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    
    page = int(page)
    posts = posts[(page - 1) * int(params['no_of_posts']) : (page - 1) * int(params['no_of_posts']) + int(params['no_of_posts'])]

    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    
    return render_template('index.html', params = params, posts = posts, prev = prev, next = next)

@app.route("/about")
def about():
    return render_template('about.html', params = params)

@app.route("/contact" , methods = ['GET' , 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, email=email, phone_num=phone, msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
        sender=email, 
        recipients=[params['gmail_user']],
        body=message + "\n" + phone)
    return render_template('contact.html', params = params)

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params = params, post = post)

@app.route("/dashboard", methods = ['GET','POST'])
def login():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts = posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if username == params['admin_user'] and password == params['admin_password']:
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params,posts = posts)

    return render_template('login.html',params=params)

@app.route("/edit/<string:sno>",methods = ['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_name = request.form.get('img_name')

            if sno == "0":
                post = Posts(title = title, slug=slug, content = content, tagline=tline, img_name=img_name, date=datetime.now())
                db.session.add(post)
                db.session.commit()
            
            else:
                post = Posts.query.filter_by(sno = sno).first()
                post.title = title
                post.slug = slug
                post.tagline = tline
                post.content = content
                post.img_name = img_name
                post.date = datetime.now()
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Posts.query.filter_by(sno=sno).first()

        return render_template('edit.html', params=params,sno=sno,post=post)



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")
    

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


@app.route("/tutorial")
def tutorial():
    tuts = Tut.query.filter_by().all()
    return render_template('tut.html',params=params,tuts=tuts)

@app.route("/tpoint")
def tpoint():
    return render_template('tpoint.html',params=params)

app.run(debug=True)