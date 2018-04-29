#encoding:utf-8
from flask import Flask,render_template,request,redirect,url_for,session
import config
from models import User,Article,Comment
from exts import db
import re

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
isvalid = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')


@app.route('/')
def index():
    context={
        'articles':Article.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('Email')
        password = request.form.get('Password')
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


@app.route('/newblog/',methods=['POST','GET'])
def newblog():
    if request.method=='GET':
        return render_template('editblog.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        article = Article(title=title, content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id==user_id).first()
        article.author = user
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/detail/<article_id>/')
def detail(article_id):
    content={
    'article':Article.query.filter(Article.id == article_id).first(),
    'comments' : Comment.query.filter(Comment.article_id==article_id).all()
    }
    return render_template('detail.html', **content)


@app.route('/add_comment/', methods=['POST'])
def add_comment():
    content = request.form.get('comment_content')
    article_id = request.form.get('article_id')
    comment = Comment(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    comment.author = user
    article = Article.query.filter(Article.id == article_id).first()
    comment.article = article
    db.session.add(comment)
    db.session.commit()
    print(comment.author)
    print(comment.article)
    return redirect(url_for('detail', article_id=article_id))


@app.context_processor
def getuser():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return{'user': user}
    return {}


if __name__ == '__main__':
    app.run()
