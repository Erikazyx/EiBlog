#encoding:utf-8
from flask import Flask,render_template,request,redirect,url_for,session
import config
from models import User
from exts import db
import re

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
isvalid = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('Email')
        print(email)
        password = request.form.get('Password')
        print(password)
        user = User.query.filter(User.email==email, User.password==password).first()
        if user:
            session['user_id']=user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'用户名或密码错误 请重试'


@app.route('/register/',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email=request.form.get('Email').lower()
        username=request.form.get('Username')
        password1=request.form.get('Password1')
        password2=request.form.get('Password2')

        if not username or not email or not password1 or not password2:
            return u'任意项都不能为空'
        if not isvalid.match(email):
            return u'该邮箱不合法'
        user = User.query.filter(User.email ==email).first()
        if user:
            return u'该邮箱已被注册'
        else:
            if password1 != password2:
                return u'两次输入密码不同，请重试'
            else:
                user=User(email=email, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.context_processor
def getuser():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return{'user':user}
    return {}


if __name__ == '__main__':
    app.run()
