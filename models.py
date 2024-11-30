from datetime import datetime
from enum import Enum
from enums import FeedbackType, PaymentStatus
from app import db, app

class BaseModel(db.Model):
    __abstract__ = True  # This makes it an abstract class, not a table in the database

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Ensure it's not nullable
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Ensure it's not nullable

    def __init__(self, *args, **kwargs):
        # Set default values for fields if not passed explicitly
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        if 'modified_at' not in kwargs:
            kwargs['modified_at'] = datetime.utcnow()

        super().__init__(*args, **kwargs)
        
class Admin(BaseModel):
    __tablename__ = 'admin'
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=True)  # Made nullable

class Customer(BaseModel):
    __tablename__ = 'customer'
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=True)  # Made nullable
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(300), nullable=True)  # Made nullable
    pincode = db.Column(db.String(300), nullable=True)  # Made nullable

class Service(BaseModel):
    __tablename__ = 'service'
    name = db.Column(db.String(150), nullable=False)
    base_price = db.Column(db.Float, nullable=True)  # Made nullable
    time_required = db.Column(db.String(50), nullable=True)  # Made nullable
    description = db.Column(db.Text, nullable=True)  # Made nullable
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    service_type_id= db.Column(db.Integer, nullable=True)  # Made nullable
    professional = db.relationship('ServiceProfessional', backref='services', lazy=True)

class ServiceProfessional(BaseModel):
    __tablename__ = 'service_professional'
    username = db.Column(db.String(150), unique=False, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)  # Made nullable
    email = db.Column(db.String(150), unique=True, nullable=True)  # Made nullable
    phone = db.Column(db.String(20), unique=True, nullable=True)  # Made nullable
    experience = db.Column(db.Integer, nullable=True)  # Made nullable
    description = db.Column(db.Text, nullable=True)  # Made nullable
    approved = db.Column(db.Boolean, default=False, nullable=True)  # Made nullable
    service_type_id = db.Column(db.Integer, nullable=False)

class ServiceRequest(BaseModel):
    __tablename__ = 'service_request'
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # Made nullable
    service_name = db.Column(db.String(50), nullable=False)  # Made nullable
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)  # Made nullable
    date_of_completion = db.Column(db.DateTime, nullable=True)  # Made nullable
    service_status = db.Column(db.String(50), default="requested", nullable=True)  # Made nullable
    service_type_id= db.Column(db.Integer, nullable=False)  
    remarks = db.Column(db.Text, nullable=True)  # Made nullable
    rejected_by_professional_id= db.Column(db.Integer, nullable=True)  # Made nullable
    rating = db.Column(db.Text, nullable=True)  # Made nullable
    payment = db.relationship('Payment', backref='service_request', lazy=True)

class Feedback(BaseModel):
    __tablename__ = 'feedback'
    type = db.Column(db.Enum(FeedbackType), nullable=False)  # Enum to differentiate between service and professional feedback
    rating = db.Column(db.Integer, nullable=False)  # Example: 1-5 stars
    comment = db.Column(db.Text, nullable=True)  # Made nullable
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # Made nullable
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)  # Made nullable

    customer = db.relationship('Customer', backref=db.backref('feedbacks', lazy=True))
    service = db.relationship('Service', backref=db.backref('feedbacks', lazy=True))
    professional = db.relationship('ServiceProfessional', backref=db.backref('feedbacks', lazy=True))

class Payment(BaseModel):
    __tablename__ = 'payment'
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    amount = db.Column(db.Float, nullable=True)  # Made nullable
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)  # Made nullable
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=True)  # Made nullable
    payment_method = db.Column(db.String(50), nullable=True)  # Made nullable
