import re
from app import db
from flask import render_template, request, redirect, url_for, session, jsonify
from app.decorators import login_required, Page
from app.models import User, Article, Comment, Category
from app.home import main


@main.route("/")
def index():
    authors = {}
    page = request.args.get("page", 1, type=int)
    pagination = Article.query.order_by(Article.create_time.desc()).paginate(
        page, per_page=10, error_out=False
    )
    articles = pagination.items
    if articles:
        for article in articles:
            author = User.query.filter(User.id == article.author_id).first().username
            authors[article.author_id] = author

    context = {"articles": articles, "authors": authors, "pagination": pagination}
    return render_template("index.html", **context)


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@main.route("/search_articles/<search_type>/<item>", methods=["GET"])
def search_article(search_type, item, *, page="1"):
    type_ = search_type
    item_ = item
    page_index = get_page_index(page)
    if search_type == "tag":
        articles = []
        all_articles = Article.query.order_by(db.desc(Article.id)).all()
        for article in all_articles:
            tags = re.split(r"\s*,\s*", str(article.tags))
            if item in tags:
                articles.append(article)
        article_count = len(articles)
    else:
        articles = (
            Article.query.filter(Article.category_id == item)
            .order_by(db.desc(Article.id))
            .all()
        )
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
        articles = articles[page.offset : page.limit]
    context = {
        "articles": articles,
        "authors": authors,
        "type_": type_,
        "item_": item_,
        "pagination": page,
    }
    return render_template("search_article.html", **context)


@main.route("/detail/<article_id>/")
def detail(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    author = User.query.filter(User.id == article.author_id).first()
    category = Category.query.filter(Category.id == article.category_id).first()
    comment_author = {}
    reply_dict = {}
    tag_list = []
    reply_list = {}
    page = request.args.get("page", 1, type=int)
    comments_count = Comment.query.filter(Comment.article_id == article_id).count()
    comments = Comment.query.filter(Comment.article_id == article_id).order_by(
        Comment.create_time.desc()
    )
    if comments:
        for comment in comments:
            comment_author[comment.author_id] = (
                User.query.filter(User.id == comment.author_id).first().username
            )
            if comment.parent_id:
                reply_dict.setdefault(comment.root_id, []).append(comment.id)
                reply_list[comment.id] = comment
    pagination = (
        Comment.query.filter(
            Comment.article_id == article_id, Comment.parent_id == None
        )
        .order_by(db.desc(Comment.create_time))
        .paginate(page, per_page=5, error_out=False)
    )
    comments = pagination.items
    if article.tags:
        tag_list = re.split(r"\s*,\s*", article.tags)

    context = {
        "article": article,
        "author": author,
        "comments": comments,
        "comments_count": comments_count,
        "comment_author": comment_author,
        "category": category,
        "tags": tag_list,
        "pagination": pagination,
        "reply_dict": reply_dict,
        "reply": reply_list,
    }
    return render_template("detail.html", **context)


@main.route("/add_comment/", methods=["POST"])
@login_required
def add_comment():
    content = request.form.get("comment_content")
    if not content:
        return u"评论不能为空"
    article_id = request.form.get("article_id")
    user_id = session["user_id"]
    comment = Comment(content=content, article_id=article_id, author_id=user_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("main.detail", article_id=article_id))


@main.route("/add_reply/", methods=["POST"])
@login_required
def add_reply():
    content = request.form.get("content")
    content = content.split(":")[1] if len(content.split(":")) > 1 else content
    reply_to = request.form.get("reply_to")
    parent_id = request.form.get("parent")
    root_id = request.form.get("root")
    article_id = request.form.get("article_id")
    message = request.form.get('message')
    print(message)
    if not root_id:
        root_id = parent_id
    author_id = session["user_id"]
    comment = Comment(
        content=content,
        reply_to=reply_to,
        parent_id=parent_id,
        root_id=root_id,
        author_id=author_id,
        article_id=article_id,
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"status": "SUCCESS"})
