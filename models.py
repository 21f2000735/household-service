from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceProfessional(db.Model):
    __tablename__ = 'service_professional'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), default="requested")
    remarks = db.Column(db.Text, nullable=True)

    service = db.relationship('Service', backref=db.backref('requests', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('requests', lazy=True))
    professional = db.relationship('ServiceProfessional', backref=db.backref('requests', lazy=True))

# Initialize the database
with app.app_context():
    db.create_all()

    # Add default admin
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin', password_hash=generate_password_hash('admin'), name="Admin")
        db.session.add(admin)

    # Add a sample customer
    customer = Customer.query.filter_by(username='cust').first()
    if not customer:
        customer = Customer(
            username='cust',
            password_hash=generate_password_hash('admin'),
            name='Tanya Goyal',
            email='tanya@gmail.com',
            phone='1234567890',
            address='Delhi 110051'
        )
        db.session.add(customer)

    # Add a sample service professional
    professional = ServiceProfessional.query.filter_by(username='pro').first()
    if not professional:
        professional = ServiceProfessional(
            username='pro',
            password_hash=generate_password_hash('admin'),
            name='Jatin Goyal',
            email='jatingoyal@gmail.com',
            phone='0987654321',
            service_type='Plumbing',
            experience=10,
            description='Expert in plumbing repairs and installations',
            approved=True
        )
        db.session.add(professional)

    # Add a sample service
    service = Service.query.filter_by(name='Basic Plumbing').first()
    if not service:
        service = Service(
            name='Basic Plumbing',
            base_price=500.0,
            time_required='2 hours',
            description='Basic plumbing services including pipe and faucet repairs'
        )
        db.session.add(service)

    # Add a sample service request
    service_request = ServiceRequest.query.filter_by(customer_id=1, service_id=1).first()
    if not service_request:
        service_request = ServiceRequest(
            service_id=service.id,
            customer_id=customer.id,
            professional_id=professional.id,
            service_status='requested',
            remarks='Urgent plumbing issue in the bathroom'
        )
        db.session.add(service_request)

    # Commit all changes
    db.session.commit()

    print("Sample entries added to Admin, Customer, ServiceProfessional, Service, and ServiceRequest tables.")
