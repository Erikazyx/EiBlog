# encoding:utf-8
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

import config


app = Flask(__name__)
db = SQLAlchemy()


def create_app():
    from decorators import is_none
    from api import home
    app.add_template_filter(is_none, 'is_none')
    app.config.from_object(config)
    db.init_app(app)
    return app


@app.context_processor
def getuser():
    from models import User
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return{'user': user}
    return {}


@app.context_processor
def get_categorys_and_tags():
    from models import Category, Tag
    categorys = Category.query.all()
    tags = Tag.query.all()
    return {'nav_category': categorys, 'nav_tags': tags}
