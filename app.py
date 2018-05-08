# encoding:utf-8
import re
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

import config
from decorators import login_required, admin_required, is_none, Page
from models import User, Article, Comment, Category, Tag


app = Flask(__name__)

app.add_template_filter(is_none, 'is_none')
app.config.from_object(config)

db = SQLAlchemy()
db.init_app(app)
isvalid = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')


@app.route('/')
def index():
    authors = {}
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.order_by(Article.create_time.desc()).paginate(page, per_page=10, error_out=False)
    articles = pagination.items
    if articles:
        for article in articles:
            author = User.query.filter(User.id == article.author_id).first().username
            authors[article.id] = author

    context = {
        'articles': articles,
        'authors': authors,
        'pagination': pagination,
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
            flash('任意项都不能为空')
            return render_template('register.html')
        if not isvalid.match(email):
            flash('请输入合法的邮箱地址')
            return render_template('register.html')
        user = User.query.filter(User.email == email).first()
        user_name = User.query.filter(User.username == username).first()
        if user_name:
            flash('该用户名已被使用')
            return render_template('register.html')
        if user:
            flash('该邮箱已被注册')
            return render_template('register.html')
        else:
            if password1 != password2:
                flash('两次输入密码不同，请重试')
                return render_template('register.html')
            else:
                user = User(email=email, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin/')
@admin_required
def admin():
    authors = {}
    category = {}
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.order_by(Article.create_time.desc()).paginate(page, per_page=20, error_out=False)
    articles = pagination.items

    if articles:
        for article in articles:
            author = User.query.filter(User.id == article.author_id).first().username
            if article.category_id:
                category_name = Category.query.filter(Category.id == article.category_id).first().name
            else:
                category_name = '未分类'
            authors[article.id] = author
            category[article.id] = category_name

    context = {
        'articles': articles,
        'authors': authors,
        'pagination': pagination,
        'categorys': category
    }
    return render_template('admin.html', **context)


@app.route('/manage_comments/')
@admin_required
def manage_comments():
    author = {}
    article = {}
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.create_time.desc()).paginate(page, per_page=20, error_out=False)
    comments = pagination.items
    if comments:
        for comment in comments:
            author[comment.id] = User.query.filter(User.id == Comment.author_id).first().username
            article[comment.id] = Article.query.filter(Article.id == Comment.article_id).first().title
    return render_template('manage_comments.html', comments=comments, authors=author,
                           article=article, pagination=pagination)


@app.route('/manage_users/')
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page, per_page=20, error_out=False)
    users = pagination.items
    return render_template('manage_users.html', users=users, pagination=pagination)


@app.route('/manage_categorys/')
@admin_required
def manage_categorys():
    categorys = Category.query.all()
    return render_template('manage_categorys.html', categorys=categorys)


@app.route('/new_blog/', methods=['GET', 'POST'])
@admin_required
def new_blog():
    if request.method == 'GET':
        categorys = Category.query.all()
        return render_template('new_editor.html', categorys=categorys)
    else:
        title = request.form.get('title')
        if not title:
            return u'标题不能为空'
        content = request.form.get('content')
        tags = request.form.get('tags')
        tag_list = re.split(r'\s*,\s*', tags)
        current_tag = Tag.query.all()
        T = []
        for tag in current_tag:
            T.append(tag.name)
        for tag in tag_list:
            if tag not in T:
                db.session.add(Tag(name=tag))
        user_id = session.get('user_id')
        category_id = request.form.get('category_id')
        article = Article(title=title, content=content, author_id=user_id, category_id=category_id, tags=tags)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('detail', article_id=article.id))


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@app.route('/search_articles/<search_type>/<item>', methods=['GET'])
def search_article(search_type, item, *, page='1'):
    type_ = search_type
    item_ = item
    page_index = get_page_index(page)
    if search_type == 'tag':
        articles = []
        all_articles = Article.query.all()
        for article in all_articles:
            tags = re.split(r'\s*,\s*', str(article.tags))
            if item in tags:
                articles.append(article)
        article_count = len(articles)
    else:
        articles = Article.query.filter(Article.category_id == item).order_by(db.desc(Article.id)).all()
        article_count = Article.query.filter(Article.category_id == item).count()
    page = Page(article_count, page_index)
    authors = {}
    if articles:
        for article in articles:
            author = User.query.filter(User.id == article.author_id).first().username
            authors[article.id] = author
    if article_count == 0:
        articles = []
    else:
        articles = articles[page.offset: page.limit]
    context = {
        'articles': articles,
        'authors': authors,
        'type_': type_,
        'item_': item_,
        'pagination': page
    }
    return render_template('search_article.html', **context)


@app.route('/add_category/', methods=['POST'])
def add_category():
    category_name = request.form.get('category_name')
    category = Category(name=category_name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('new_blog'))


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
        if not article.title:
            return u'标题不能为空'
        article.content = request.form.get('content')
        if not article.content:
            return u'文章不能为空'
        article.tags = request.form.get('tags')
        article.category_id = request.form.get('category_id')
        article.edit_time = datetime.now()
        db.session.commit()
        return redirect(url_for('detail', article_id=article_id))


@app.route('/delete/<item_name>/<item_id>/')
@admin_required
def delete_action(item_id, item_name):
    if item_name == 'comment':
        item = Comment.query.filter(Comment.id == item_id).first()
    elif item_name == 'article':
        item = Article.query.filter(Article.id == item_id).first()
        comment = Comment.query.filter(Comment.article_id == item_id).all()
        for i in comment:
            db.session.delete(i)
    elif item_name == 'user':
        item = User.query.filter(User.id == item_id).first()
        comment = Comment.query.filter(Comment.author_id == item_id).all()
        article = Article.query.filter(Article.author_id == item_id).all()
        for i in article:
            db.session.delete(i)
        for i in comment:
            db.session.delete(i)
    else:
        item = Category.query.filter(Category.id == item_id).first()
        article = Article.query.filter(Article.category_id == item_id).all()
        for i in article:
            i.category_id = None
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/detail/<article_id>/')
def detail(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    author = User.query.filter(User.id == article.author_id).first()
    # comments = Comment.query.filter(Comment.article_id == article_id).order_by(db.desc(Comment.id)).all()
    category = Category.query.filter(Category.id == article.category_id).first()
    comment_author = {}
    tag_list = []
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.create_time.desc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    if article.tags:
        tag_list = re.split(r'\s*,\s*', article.tags)
    if comments:
        for comment in comments:
            comment_author[comment.id] = User.query.filter(User.id == comment.author_id).first().username
    context = {
        'article': article,
        'author': author,
        'comments': comments,
        'comment_author': comment_author,
        'category': category,
        'tags': tag_list,
        'pagination': pagination,
    }
    return render_template('detail.html', **context)


@app.route('/add_comment/', methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('comment_content')
    if not content:
        return u'评论不能为空'
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


@app.context_processor
def get_categorys_and_tags():
    categorys = Category.query.all()
    tags = Tag.query.all()
    return {'nav_category': categorys, 'nav_tags': tags}
