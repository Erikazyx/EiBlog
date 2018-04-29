from flask import redirect, session, url_for
from functools import wraps
from models import User


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_id'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            is_admin = User.query.filter(User.id == user_id).first().admin
            if is_admin:
                return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper
