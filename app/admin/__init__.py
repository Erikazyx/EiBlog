from flask import  Blueprint

test = Blueprint('test', __name__)
from app.admin import  views