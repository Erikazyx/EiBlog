from app.auth import auth
from .form import Login, UserForm, ChangePwd
from flask import session, redirect, url_for, render_template, flash
from app.models import User
from app import db
from app.decorators import login_required


@auth.route("/login/", methods=["GET", "POST"])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.index'))
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter(User.email == email).first()
        if not user or not user.verify_password(password):
            flash("用户名或密码错误 请重试")
        else:
            session["user_id"] = user.id
            session.permanent = True
            return redirect(url_for("main.index"))
    return render_template("login.html", form=form)


@auth.route("/register/", methods=["GET", "POST"])
def register():
    if session.get('user_id'):
        return redirect(url_for('main.index'))
    form = UserForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.query.filter(User.email == email).first()
        user_name = User.query.filter(User.username == username).first()
        if user_name:
            flash("该用户名已被使用")
            return render_template("register.html", form=form)
        if user:
            flash("该邮箱已被注册")
            return render_template("register.html", form=form)
        user = User(email=email, username=username, password_gen=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    else:
        return render_template("register.html", form=form)


@login_required
@auth.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@login_required
@auth.route('/change_pwd/',methods=['post','get'])
def change_pwd():
    form = ChangePwd()
    if form.validate_on_submit():
        old_pwd = form.old_password.data
        user_id = session['user_id']
        user = User.query.filter(User.id == user_id).first()
        if not user.verify_password(old_pwd):
            flash('原密码错误,请重试')
            return render_template('change_pwd.html', form=form)
        password = form.password1.data
        user.password = password
        user.password_gen = password
        db.session.add(user)
        db.session.commit()
        session.clear()
        flash('更改密码成功，请重新登陆')
        return redirect(url_for("auth.login"))
    else:
        return render_template('change_pwd.html', form=form)
