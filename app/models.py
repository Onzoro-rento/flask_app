from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120),unique = True, nullable = True)
    travel_plan = relationship("TravelPlan", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    confirmation_pdf = db.Column(db.String(200), nullable=True)
    estimated_budget = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)

    destinations = db.relationship('Destination', backref='travel_plan', cascade="all, delete-orphan")
    hotel_url = db.relationship('Hotel_url', backref='travel_plan', cascade="all, delete-orphan")
    pdf_files = db.relationship('PDFFile', backref='travel_plan', cascade="all, delete-orphan")
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name="fk_plans_users"), nullable=False)
    user = relationship("User", back_populates="travel_plan")


class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)


class Hotel_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_url = db.Column(db.String(200), nullable=True)
    order_hotel = db.Column(db.Integer, nullable=False)
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)


class PDFFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    order_pdf = db.Column(db.Integer, nullable=False)
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), nullable=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'), index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
