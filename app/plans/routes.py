import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import TravelPlan, Destination, Hotel_url, PDFFile
from . import plans_bp

@plans_bp.route('/index')
@login_required
def index():
    travel_plans = TravelPlan.query\
    .filter_by(user_id=current_user.id,is_completed = False)\
    .order_by(TravelPlan.start_date.desc())\
    .all()
    return render_template('plans/index.html', travel_plans=travel_plans)

@plans_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    if request.method == 'POST':
        plan_name = request.form['plan_name']
        destination = request.form['destination']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        notes = request.form['notes']
        estimated_budget = request.form.get('estimated_budget', type=float)
        actual_cost = request.form.get('actual_cost', type=float)
        confirmation_pdf = None

        if 'confirmation_pdf' in request.files:
            pdf_file = request.files['confirmation_pdf']
            if pdf_file.filename != '':
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(os.path.join('static', 'uploads'), filename).replace("\\", "/")
                pdf_file.save(pdf_path)
                confirmation_pdf = os.path.join('uploads', filename).replace("\\", "/")

        new_plan = TravelPlan(
            plan_name=plan_name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            estimated_budget=estimated_budget,
            actual_cost=actual_cost,
            confirmation_pdf=confirmation_pdf,
            user_id=current_user.id
        )
        db.session.add(new_plan)
        db.session.commit()

        hotel_urls = request.form.getlist('hotel_urls[]')
        for order_hotel, hotel_url in enumerate(hotel_urls):
            if hotel_url.strip():
                new_hotel_url = Hotel_url(hotel_url=hotel_url.strip(), order_hotel=order_hotel + 1, travel_plan_id=new_plan.id)
                db.session.add(new_hotel_url)

        destinations = request.form.getlist('destinations[]')
        for order, name in enumerate(destinations):
            if name.strip():
                new_destination = Destination(name=name.strip(), order=order + 1, travel_plan_id=new_plan.id)
                db.session.add(new_destination)

        pdf_files = request.files.getlist('pdf_files[]')
        for order_pdf, pdf_file in enumerate(pdf_files):
            if pdf_file and pdf_file.filename != '':
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(os.path.join('static', 'uploads'), filename).replace("\\", "/")
                pdf_file.save(pdf_path)
                new_pdf = PDFFile(filename=os.path.join('uploads', filename).replace("\\", "/"),
                                  order_pdf=order_pdf + 1,
                                  travel_plan_id=new_plan.id)
                db.session.add(new_pdf)

        db.session.commit()
        return redirect(url_for('plans.index'))

    return render_template('plans/create_plan.html')

@plans_bp.route('/plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    plan = TravelPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    return render_template('plans/view_plan.html', plan=plan)

@plans_bp.route('/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = TravelPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    if plan.confirmation_pdf:
        pdf_path = os.path.join(os.path.join('static', 'uploads'), os.path.basename(plan.confirmation_pdf))
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    db.session.delete(plan)
    db.session.commit()
    return redirect(url_for('plans.index'))

@plans_bp.route('/update/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def update(plan_id):
    current_plan = TravelPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        current_plan.plan_name = request.form['plan_name']
        current_plan.destination = request.form['destination']
        current_plan.start_date = request.form['start_date']
        current_plan.end_date = request.form['end_date']
        current_plan.notes = request.form['notes']
        current_plan.estimated_budget = request.form.get('estimated_budget', type=float)
        current_plan.actual_cost = request.form.get('actual_cost', type=float)
        current_plan.confirmation_pdf = None

        current_plan.pdf_files.clear()
        pdf_files = request.files.getlist('pdf_files[]')
        for order_pdf, pdf_file in enumerate(pdf_files):
            if pdf_file and pdf_file.filename != '':
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(os.path.join('static', 'uploads'), filename).replace("\\", "/")
                pdf_file.save(pdf_path)
                new_pdf = PDFFile(filename=os.path.join('uploads', filename).replace("\\", "/"),
                                  order_pdf=order_pdf + 1,
                                  travel_plan_id=current_plan.id)
                db.session.add(new_pdf)

        current_plan.destinations.clear()
        destinations = request.form.getlist('destinations[]')
        for order, name in enumerate(destinations):
            if name.strip():
                new_destination = Destination(name=name.strip(), order=order + 1, travel_plan_id=current_plan.id)
                db.session.add(new_destination)

        current_plan.hotel_url.clear()
        hotel_urls = request.form.getlist('hotel_urls[]')
        for order_hotel, hotel_url in enumerate(hotel_urls):
            if hotel_url.strip():
                new_hotel = Hotel_url(hotel_url=hotel_url.strip(), order_hotel=order_hotel + 1, travel_plan_id=current_plan.id)
                db.session.add(new_hotel)

        db.session.commit()
        flash("変更しました")
        return redirect(url_for('plans.index'))

    return render_template("plans/update_form.html", edit_id=current_plan.id, current_plan=current_plan)

@plans_bp.route('/plans/complete/<int:plan_id>', methods=['POST'])
@login_required
def mark_complete(plan_id):
    plan = TravelPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        abort(403)
    plan.is_completed = True
    db.session.commit()
    flash('対象の旅行を完了しました')
    return redirect(url_for('plans.index'))
