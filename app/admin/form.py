from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class ArticleForm(FlaskForm):
    title = StringField(u"标题", validators=[DataRequired(u'标题不能为空')])
    tags = StringField(u"标签")
    content = PageDownField(u"正文", validators=[DataRequired(u'必须有正文')])
    category = SelectField(u"分类", coerce=int)
    submit = SubmitField(u"发布")
