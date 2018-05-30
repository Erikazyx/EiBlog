import re
from app import db
from flask import render_template, request, redirect, url_for, session, flash
from app.decorators import login_required, Page
from app.models import User, Article, Comment, Category

from app.home import main
isvalid = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')



@main.route('/')
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


@main.route('/login/', methods=['GET', 'POST'])
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
            return redirect(url_for('main.index'))
        else:
            return u'用户名或密码错误 请重试'


@main.route('/register/', methods=['GET', 'POST'])
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
                return redirect(url_for('main.login'))


@main.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@main.route('/search_articles/<search_type>/<item>', methods=['GET'])
def search_article(search_type, item, *, page='1'):
    type_ = search_type
    item_ = item
    page_index = get_page_index(page)
    if search_type == 'tag':
        articles = []
        all_articles = Article.query.order_by(db.desc(Article.id)).all()
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


@main.route('/detail/<article_id>/')
def detail(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    author = User.query.filter(User.id == article.author_id).first()
    category = Category.query.filter(Category.id == article.category_id).first()
    comment_author = {}
    tag_list = []
    page = request.args.get('page', 1, type=int)
    comments_count = Comment.query.filter(Comment.article_id == article_id).count()
    pagination = Comment.query.filter(Comment.article_id == article_id).order_by(Comment.create_time.desc()).paginate(
        page, per_page=5, error_out=False)
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
        'comments_count': comments_count,
        'comment_author': comment_author,
        'category': category,
        'tags': tag_list,
        'pagination': pagination,
    }
    return render_template('detail.html', **context)


@main.route('/add_comment/', methods=['POST'])
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
    return redirect(url_for('main.detail', article_id=article_id))
