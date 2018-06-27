from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email, Length


class UserForm(FlaskForm):
    email = StringField(u'邮箱', [DataRequired(u'请输入邮箱'), Email(u'请输入合法的邮箱')],
                        render_kw={"placeholder": "example@example.com"})
    username = StringField(u"用户名", validators=[DataRequired(u'用户名不能为空'), Length(0, 24, u'用户名过长')],
                           render_kw={"placeholder": "Your name"})
    password = PasswordField(u"密码", [DataRequired(u'请设置密码'), Length(6, 24, u'密码过短或过长'),
                                     EqualTo('password2', message=u'两次输入密码不一致！')])
    password2 = PasswordField(u"确认密码", validators=[DataRequired(u'必须确认密码')])
    submit = SubmitField(u"注册")


class Login(FlaskForm):
    email = StringField(u'邮箱', [DataRequired(u'请输入邮箱')])
    password = PasswordField(u'密码', [DataRequired(u'请输入密码')])
    submit = SubmitField(u"登录")


class ChangePwd(FlaskForm):
    old_password = PasswordField(u'原密码', [DataRequired(u'输入原密码')])
    password1 = PasswordField(u'新密码', [DataRequired(u'输入新密码'), Length(6, 24, u'新密码请在6-24个字符之间'),
                                       EqualTo('password2', message=u'两次密码输入不一致')])
    password2 = PasswordField(u'确认新密码', [DataRequired(u'确认新密码')])
    submit = SubmitField(u"确认修改")
