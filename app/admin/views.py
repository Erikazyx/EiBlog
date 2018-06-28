import re
from datetime import datetime
from app import db
from flask import render_template, request, redirect, url_for, session, flash
from app.decorators import admin_required
from app.models import User, Article, Comment, Category, Tag
from .form import ArticleForm
from app.admin import admin


@admin.route('/new_blog/', methods=['GET', 'POST'])
@admin_required
def new_blog():
    form = ArticleForm()
    categorys = [(c.id, c.name) for c in Category.query.all()]
    form.category.choices = categorys
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tags = form.tags.data
        tag_list = re.split(r'\s*,\s*', tags)
        current_tag = Tag.query.all()
        T = []
        for tag in current_tag:
            T.append(tag.name)
        for tag in tag_list:
            if tag not in T:
                db.session.add(Tag(name=tag, count=1))
        category_id = form.category.data
        user_id = session.get('user_id')
        article = Article(title=title, content=content, author_id=user_id, category_id=category_id, tags=tags)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.detail', article_id=article.id))
    return render_template('markdown.html', form=form)


@admin.route('/edit_blog/<article_id>', methods=['POST', 'GET'])
@admin_required
def edit_blog(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    form = ArticleForm()
    categorys = [(c.id, c.name) for c in Category.query.all()]
    form.category.choices = categorys
    if form.validate_on_submit():
        categorys = [(c.id, c.name) for c in Category.query.all()]
        form.category.choices = categorys

        article.title = form.title.data
        article.content = form.content.data
        article.tags = form.tags.data
        article.edit_time = datetime.utcnow()
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.detail', article_id=article.id))
    form.category.data = article.category_id
    form.title.data = article.title
    form.content.data = article.content
    form.tags.data = article.tags
    return render_template('markdown.html', form=form)


@admin.route('/add_category/', methods=['POST'])
@admin_required
def add_category():
    category_name = request.form.get('category_name')
    category = Category(name=category_name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('admin.manage_categorys'))


@admin.route('/del_comment/<comment_id>/')
@admin_required
def delete_comment(comment_id, *, n='null'):
    del_comment = Comment.query.filter(Comment.id == comment_id).first()
    if del_comment:
        if n == 'all':
            child = Comment.query.filter((Comment.root_id == comment_id) | (Comment.parent_id == comment_id)).all()
        else:
            child = Comment.query.filter(Comment.root_id == comment_id).all()
        article_id = del_comment.article_id
        for i in child:
            db.session.delete(i)
        db.session.delete(del_comment)
        db.session.commit()
    else:
        flash('非法操作')
        return redirect(url_for('main.index'))
    return redirect(url_for('main.detail', article_id=article_id))


@admin.route('/del_article/<article_id>/')
@admin_required
def delete_article(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    if article:
        comments = Comment.query.filter(Comment.article_id == article_id).all()
        if article.tags:
            del_tag(article.tags)
        for single_comment in comments:
            delete_comment(single_comment.id)
        db.session.delete(article)
        db.session.commit()
    else:
        flash('非法操作')
    return redirect(url_for('main.index'))


def del_tag(tag):
    tag_list = re.split(r'\s*,\s*', tag)
    for tag in tag_list:
        T = Tag.query.filter(Tag.name == tag).first()
        if T and T.count == 1:
            db.session.delete(T)
        else:
            T.count -= 1


@admin.route('/del_user/<user_id>/')
@admin_required
def delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if user:
        comments = Comment.query.filter(Comment.author_id == user_id).all()
        articles = Article.query.filter(Article.author_id == user_id).all()
        if articles:
            for i in articles:
                delete_article(i.id)
        if comments:
            for i in comments:
                delete_comment(i.id, n='all')
        db.session.delete(user)
        db.session.commit()
    else:
        flash('非法操作')
    return redirect(url_for('admin.manage_users'))


@admin.route('/del_category/<category_id>/')
@admin_required
def delete_category(category_id):
    category = Category.query.filter(Category.id == category_id).first()
    if category:
        article = Article.query.filter(Article.category_id == category_id).all()
        for i in article:
            i.category_id = None
        db.session.delete(category)
        db.session.commit()
    else:
        flash('非法操作')
    return redirect(url_for('admin.manage_categorys'))


@admin.route('/admin/')
@admin_required
def admin_page():
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
            authors[article.author_id] = author
            category[article.category_id] = category_name

    context = {
        'articles': articles,
        'authors': authors,
        'pagination': pagination,
        'categorys': category
    }
    return render_template('admin/admin.html', **context)


@admin.route('/manage_comments/')
@admin_required
def manage_comments():
    author = {}
    article = {}
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.create_time.desc()).paginate(page, per_page=20, error_out=False)
    comments = pagination.items
    if comments:
        for comment in comments:
            author[comment.author_id] = User.query.filter(User.id == comment.author_id).first().username
            article[comment.article_id] = Article.query.filter(Article.id == Comment.article_id).first().title
    return render_template('admin/manage_comments.html', comments=comments, author=author,
                           article=article, pagination=pagination)


@admin.route('/manage_users/')
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page, per_page=20, error_out=False)
    users = pagination.items
    return render_template('admin/manage_users.html', users=users, pagination=pagination)


@admin.route('/manage_categorys/')
@admin_required
def manage_categorys():
    categorys = Category.query.all()
    return render_template('admin/manage_categorys.html', categorys=categorys)
