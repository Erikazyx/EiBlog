# encoding:utf-8
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown

import config

pagedown = PageDown()
app = Flask(__name__)
db = SQLAlchemy()


def create_app():
    from app.decorators import is_none
    app.add_template_filter(is_none, 'is_none')
    app.config.from_object(config)
    db.init_app(app)
    from app.home import main as main_blueprint
    from app.admin import admin as admin_blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint, )
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(auth_blueprint)
    pagedown.init_app(app)
    return app


@app.context_processor
def getuser():
    from app.models import User
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return{'user': user}
    return {}


@app.context_processor
def get_categorys_and_tags():
    from app.models import Category, Tag
    categorys = Category.query.all()
    tags = Tag.query.all()
    return {'nav_category': categorys, 'nav_tags': tags}
