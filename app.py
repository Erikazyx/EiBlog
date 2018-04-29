#encoding:utf-8
from flask import Flask, render_template, request, redirect, url_for, session
import config
from decorators import login_required, admin_required
from models import User, Article, Comment
from exts import db
import re
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
isvalid = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')


@app.route('/')
def index():
    # context = {'articles': Article.query.order_by('-create_time').all()}
    articles = Article.query.order_by(db.desc(Article.id)).all()
    authors = {}

    if articles:
        for article in articles:
            author = User.query.filter(User.id == article.author_id).first().username
            authors[article.id] = author

    context = {
        'articles': articles,
        'authors': authors
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('Email')
        password = request.form.get('Password')
        user = User.query.filter(User.email == email, User.password == password).first()
        if user:
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'用户名或密码错误 请重试'


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('Email').lower()
        username = request.form.get('Username')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')

        if not username or not email or not password1 or not password2:
            return u'任意项都不能为空'
        if not isvalid.match(email):
            return u'该邮箱不合法'
        user = User.query.filter(User.email == email).first()
        if user:
            return u'该邮箱已被注册'
        else:
            if password1 != password2:
                return u'两次输入密码不同，请重试'
            else:
                user = User(email=email, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/new_blog/', methods=['POST', 'GET'])
@admin_required
def new_blog():
    if request.method == 'GET':
        return render_template('newblog.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = session.get('user_id')
        article = Article(title=title, content=content, author_id=user_id)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('detail', article_id=article.id))


@app.route('/edit_blog/<article_id>', methods=['POST', 'GET'])
@admin_required
def edit_blog(article_id):
    if request.method == 'GET':
        article = Article.query.filter(Article.id == article_id).first()
        return render_template('editblog.html', article=article)
    else:
        article_id = request.form.get('article_id')
        article = Article.query.filter(Article.id == article_id).first()
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.create_time = datetime.now()
        db.session.commit()
        return redirect(url_for('detail', article_id=article_id))


@app.route('/delete/<article_id>')
@admin_required
def delete_blog(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/detail/<article_id>/')
def detail(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    author = User.query.filter(User.id == article.author_id).first()
    comments = Comment.query.filter(Comment.article_id == article_id).order_by(db.desc(Comment.id)).all()
    comment_author = {}
    if comments:
        for comment in comments:
            comment_author[comment.id] = User.query.filter(User.id == comment.author_id).first().username
    context = {
        'article': article,
        'author': author,
        'comments': comments,
        'comment_author': comment_author
    }
    return render_template('detail.html', **context)


@app.route('/add_comment/', methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('comment_content')
    article_id = request.form.get('article_id')
    user_id = session['user_id']
    comment = Comment(content=content, article_id=article_id, author_id=user_id)
    db.session.add(comment)
    db.session.commit()
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
