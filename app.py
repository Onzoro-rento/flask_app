import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_plans.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  

db = SQLAlchemy(app)
migrate = Migrate(app,db)


class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)#プラン名
    destination = db.Column(db.String(100), nullable=False)#目的地
    start_date = db.Column(db.String(20), nullable=False)#開始日
    end_date = db.Column(db.String(20), nullable=False) #終了日
    notes = db.Column(db.Text, nullable=True) #メモ
    ##hotel_url = db.Column(db.String(200), nullable=True) #ホテルのURL
    confirmation_pdf = db.Column(db.String(200), nullable=True) #メール確認pdf
    estimated_budget = db.Column(db.Float, nullable=True)  #予算
    actual_cost = db.Column(db.Float, nullable=True)  # 実費

    # 行き先リストとのリレーション
    destinations = db.relationship('Destination', backref='travel_plan', cascade="all, delete-orphan")
    hotel_url = db.relationship('Hotel_url',backref='travel_plan', cascade="all, delete-orphan")
    pdf_files = db.relationship('PDFFile', backref='travel_plan', cascade="all, delete-orphan")
    

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 行き先名
    order = db.Column(db.Integer, nullable=False)  # 順番
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

class Hotel_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_url = db.Column(db.String(200), nullable=True) #ホテルのURL
    order_hotel = db.Column(db.Integer, nullable=False)  
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

class PDFFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)  # ファイル名
    order_pdf = db.Column(db.Integer, nullable=False)  
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

db.create_all()

# ホームページ
@app.route('/')
def index():
    travel_plans = TravelPlan.query.all()
    return render_template('index.html', travel_plans=travel_plans)



@app.route('/create', methods=['GET', 'POST'])
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
            confirmation_pdf=confirmation_pdf
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

# プラン詳細表
@app.route('/plan/<int:plan_id>')
def view_plan(plan_id):
    plan = TravelPlan.query.get_or_404(plan_id)
    return render_template('view_plan.html', plan=plan)

# プラン削除
@app.route('/delete/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    plan = TravelPlan.query.get_or_404(plan_id)

    # PDFファイル削除
    if plan.confirmation_pdf:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(plan.confirmation_pdf))
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # データベースから削除
    db.session.delete(plan)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
