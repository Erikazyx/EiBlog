# encoding:utf-8
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


def is_none(args):
    if args:
        return args
    else:
        return u'未设定'


class Page(object):

    def __init__(self, item_count, page=1, page_size=10):
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)
        if (item_count == 0) or (page > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page = 1
        else:
            self.page = page
            self.offset = self.page_size * (page - 1)
            self.limit = self.page_size
        self.page_list = range(1, self.page_count + 1)
        self.has_next = self.page < self.page_count
        self.has_prev = self.page > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)



    __repr__ = __str__
