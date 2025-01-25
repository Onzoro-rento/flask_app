import os
from flask import Flask, render_template, request, redirect, url_for,flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required,current_user
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,PasswordField
from wtforms.validators import DataRequired,Length,ValidationError


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_plans.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  

db = SQLAlchemy(app)
migrate = Migrate(app,db)
login_manager = LoginManager()
login_manager.init_app(app)
#未認証のユーザーがアクセスしようとした際に
#リダイレクトされる関数名を設定する
login_manager.view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(50),unique = True,nullable = False)
    password = db.Column(db.String(120),nullable = False)
    
    travel_plan = relationship("TravelPlan",back_populates = "user")
    #パスワードをハッシュ化して設定する
    def set_password(self,password):
        self.password = generate_password_hash(password)
        #入力されたパスワードとハッシュ化されたパスワードの比較
    def check_password(self,password):
        return check_password_hash(self.password,password)


class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)#プラン名
    destination = db.Column(db.String(100), nullable=False)#目的地
    start_date = db.Column(db.String(20), nullable=False)#開始日
    end_date = db.Column(db.String(20), nullable=False) #終了日
    notes = db.Column(db.Text, nullable=True) #メモ
    confirmation_pdf = db.Column(db.String(200), nullable=True) #メール確認pdf
    estimated_budget = db.Column(db.Float, nullable=True)  #予算
    actual_cost = db.Column(db.Float, nullable=True)  # 実費

    # 行き先リストとのリレーション
    destinations = db.relationship('Destination', backref='travel_plan', cascade="all, delete-orphan")
    hotel_url = db.relationship('Hotel_url',backref='travel_plan', cascade="all, delete-orphan")
    pdf_files = db.relationship('PDFFile', backref='travel_plan', cascade="all, delete-orphan")
    
    user_id = db.Column(db.Integer,db.ForeignKey('users.id',name="fk_plans_users"),nullable = False)
    user = relationship("User",back_populates = "travel_plan")
    

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 行き先名
    order = db.Column(db.Integer, nullable=False)  # 順番
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

class Hotel_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_url = db.Column(db.String(200), nullable=True) #ホテルのURL
    order_hotel = db.Column(db.Integer, nullable=False)  #順番
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

class PDFFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)  # ファイル名
    order_pdf = db.Column(db.Integer, nullable=False)  # 順番
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

db.create_all()

class LoginForm(FlaskForm):
    username = StringField('ユーザー名：',validators=[DataRequired('ユーザー名は必須入力です')])
    password = PasswordField('パスワード：',validators = [Length(4,10,'パスワードの長さは4文字以上10文字以内です')])
    submit = SubmitField('ログイン')
    def validate_password(self,password):
        if not (any(c.isalpha() for c in password.data) and \
                any(c.isdigit() for c in password.data) and \
                any(c in '!@#$%^&*()' for c in password.data)):
            raise ValidationError('パスワードには【英数字と記号：!@#$%^&*()】を含める必要があります')


class SignUpForm(LoginForm):
    submit = SubmitField('サインアップ')
    
    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('そのユーザー名は既に使用されています。')
#ログイン
@app.route("/",methods = ["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            
            login_user(user)
            
            return redirect(url_for("index"))
        flash("認証不備です")
    return render_template("login_form.html",form = form)

#ログアウト
@app.route("/logout")
def logout():
    logout_user()
    flash("ログアウトしました")
    
    return redirect(url_for("login"))
#ユーザー登録
@app.route("/register",methods = ["GET","POST"])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("ユーザー登録しました")
        return redirect(url_for("login"))
    return render_template("register_form.html",form = form)

# ホームページ
@app.route('/index')
@login_required
def index():
    travel_plans = TravelPlan.query.filter_by(user_id = current_user.id).all()
    return render_template('index.html', travel_plans=travel_plans)




@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    if request.method == 'POST':
        plan_name = request.form['plan_name']
        destination = request.form['destination']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        notes = request.form['notes']
        ##hotel_url = request.form['hotel_url']
        estimated_budget = request.form.get('estimated_budget', type=float)
        actual_cost = request.form.get('actual_cost', type=float)
        confirmation_pdf = None

        # PDFアップロード処理
        if 'confirmation_pdf' in request.files:
            pdf_file = request.files['confirmation_pdf']
            if pdf_file.filename != '':
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                pdf_file.save(pdf_path)
                confirmation_pdf = os.path.join('uploads', filename).replace("\\", "/")

        # 新しいプランを作成
        new_plan = TravelPlan(
            plan_name=plan_name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            ##hotel_url=hotel_url,
            estimated_budget=estimated_budget,
            actual_cost=actual_cost,
            confirmation_pdf=confirmation_pdf,
            user_id = current_user.id
        )
        db.session.add(new_plan)
        db.session.commit()
        
        hotel_urls = request.form.getlist('hotel_urls[]')
        for order_hotel, hotel_url in enumerate(hotel_urls):
            if hotel_url.strip():
                new_hotel_url = Hotel_url(hotel_url=hotel_url.strip(), order_hotel=order_hotel + 1, travel_plan_id=new_plan.id)
                db.session.add(new_hotel_url)

        db.session.commit()
        

        # 行き先を保存
        destinations = request.form.getlist('destinations[]')
        for order, name in enumerate(destinations):
            if name.strip():
                new_destination = Destination(name=name.strip(), order=order + 1, travel_plan_id=new_plan.id)
                db.session.add(new_destination)

        db.session.commit()
        pdf_files = request.files.getlist('pdf_files[]')
        for order_pdf, pdf_file in enumerate(pdf_files):
            if pdf_file and pdf_file.filename != '':
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                pdf_file.save(pdf_path)
                new_pdf = PDFFile(filename=os.path.join('uploads', filename).replace("\\", "/"),
                                  order_pdf=order_pdf + 1,
                                  travel_plan_id=new_plan.id)
                db.session.add(new_pdf)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create_plan.html')

# プラン詳細表示
@app.route('/plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    plan = TravelPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    return render_template('view_plan.html', plan=plan)

# プラン削除
@app.route('/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = TravelPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    # PDFファイル削除
    if plan.confirmation_pdf:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(plan.confirmation_pdf))
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # データベースから削除
    db.session.delete(plan)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:plan_id>',methods = ["GET","POST"])
@login_required
def update(plan_id):
    current_plan = TravelPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        current_plan.plan_name = request.form['plan_name']
        current_plan.destination = request.form['destination']
        current_plan.start_date = request.form['start_date']
        current_plan.end_date = request.form['end_date']
        current_plan.notes = request.form['notes']
        ##hotel_url = request.form['hotel_url']
        current_plan.estimated_budget = request.form.get('estimated_budget', type=float)
        current_plan.actual_cost = request.form.get('actual_cost', type=float)
        current_plan.confirmation_pdf = None

        # PDFアップロード処理
        pdf_files = request.files.getlist('pdf_files[]')
        current_plan.pdf_files.clear()  # 既存のPDF情報を削除
        for order_pdf, pdf_file in enumerate(pdf_files):
            if pdf_file and pdf_file.filename != '':
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                pdf_file.save(pdf_path)
                new_pdf = PDFFile(filename=os.path.join('uploads', filename).replace("\\", "/"),
                                  order_pdf=order_pdf + 1,
                                  travel_plan_id=current_plan.id)
                db.session.add(new_pdf)

        # 行き先を更新
        destinations = request.form.getlist('destinations[]')
        current_plan.destinations.clear()
        for order, name in enumerate(destinations):
            if name.strip():
                new_destination = Destination(name=name.strip(), order=order + 1, travel_plan_id=current_plan.id)
                db.session.add(new_destination)

        # ホテルURLを更新
        hotel_urls = request.form.getlist('hotel_urls[]')
        current_plan.hotel_url.clear()
        for order_hotel, hotel_url in enumerate(hotel_urls):
            if hotel_url.strip():
                new_hotel = Hotel_url(hotel_url=hotel_url.strip(), order_hotel=order_hotel + 1, travel_plan_id=current_plan.id)
                db.session.add(new_hotel)

        db.session.commit()
        flash("変更しました")
        
        return redirect(url_for("index"))
    return render_template("update_form.html",edit_id = current_plan.id,current_plan=current_plan,)    

from werkzeug.exceptions import NotFound


@app.errorhandler(NotFound)
def show_404_page(error):
    msg = error.description
    print('エラー内容：',msg)
    return render_template('404.html',msg = msg),404


if __name__ == '__main__':
    app.run(debug=True)
