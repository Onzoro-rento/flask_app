from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User
from . import auth_bp
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField('ユーザー名：', validators=[DataRequired('ユーザー名は必須入力です')])
    password = PasswordField('パスワード：', validators=[Length(4, 10, 'パスワードの長さは4文字以上10文字以内です')])
    submit = SubmitField('ログイン')

    def validate_password(self, password):
        if not (any(c.isalpha() for c in password.data) and
                any(c.isdigit() for c in password.data) and
                any(c in '!@#$%^&*()' for c in password.data)):
            raise ValidationError('パスワードには【英数字と記号：!@#$%^&*()】を含める必要があります')

class SignUpForm(LoginForm):
    name = StringField('名前')
    email = StringField('Eメール',validators=[DataRequired('Eメールは必須項目です')])
    submit = SubmitField('サインアップ')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('そのユーザー名は既に使用されています。')

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('plans.index'))
        flash('認証不備です')
    return render_template('auth/login_form.html', form=form)

@auth_bp.route('/logout',methods=['POST'])
def logout():
    logout_user()
    flash('ログアウトしました')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        session['register_data'] = {
            'username':form.username.data,
            'password':form.password.data,
            'email':form.email.data,
            'name':form.name.data
        }
        
        return redirect(url_for('auth.register_confirm'))
    return render_template('auth/register_form.html', form=form)

@auth_bp.route('/register/confirm', methods=['GET'])
def register_confirm():
    data = session.get('register_data')
    if not data:
        return redirect(url_for('auth.register'))
    return render_template('auth/register_confirm.html', data=data)

@auth_bp.route('/register/final', methods=['POST'])
def register_final():
    data = session.get('register_data')
    if not data:
        flash('セッションが切れました。もう一度入力してください。')
        return redirect(url_for('auth.register'))

    user = User(
        username=data['username'],
        email=data['email'],
        name=data['name']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    session.pop('register_data', None)
    flash('ユーザー登録が完了しました')
    return redirect(url_for('auth.login'))
