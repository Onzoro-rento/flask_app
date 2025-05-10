from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import TravelPlan, Destination, Hotel_url, PDFFile
from . import history_bp

@history_bp.route('/history')
@login_required
def history():
    history_plans = TravelPlan.query\
        .filter_by(user_id=current_user.id, is_completed=True)\
        .order_by(TravelPlan.start_date.desc())\
        .all()
    return render_template('history/history.html', history_plans=history_plans)
