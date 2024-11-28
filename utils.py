from datetime import datetime
from werkzeug.security import generate_password_hash
from models import Admin, Customer, Service, ServiceProfessional, ServiceRequest, Payment, Feedback, FeedbackType, PaymentStatus
from app import app, db

def create_or_get_admin():
    with app.app_context():  
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(username="admin", password_hash=generate_password_hash("admin"), name="Super Admin")
            db.session.add(admin)
            db.session.commit()  # Commit after adding the admin
        return admin

def create_or_get_customer():
    with app.app_context():
        customer = Customer.query.filter_by(username="cust").first()
        if not customer:
            customer = Customer(
                username="cust",
                password_hash=generate_password_hash("admin"),
                name="Tanya Goyal",
                email="tanya@gmail.com",
                phone="1234567890",
                address="Delhi 110051",
                pincode="110051"
                )
            db.session.add(customer)
            db.session.commit()  # Commit after adding the customer
        return customer

def create_or_get_service():
    with app.app_context():  # Ensuring that the database operation happens inside the app context
        service = Service.query.filter_by(name="Plumbing").first()
        if not service:
            service = Service(
                name="Plumbing",
                base_price=500.0,
                time_required="2 hours",
                description="All types of plumbing services",
                service_type_id=1
            )
            db.session.add(service)
            db.session.commit()  # Commit after adding the service
        return service

def create_or_get_service_professional():
    with app.app_context():  # Ensures that the database operation happens inside the app context
        professional = ServiceProfessional.query.filter_by(username="pro").first()
        if not professional:
            professional = ServiceProfessional(
                username="pro",
                password_hash=generate_password_hash("admin"),
                name="Jatin Goyal",
                email="jatingoyal@gmail.com",
                phone="9876543210",
                experience=10,
                description="Expert in plumbing and repairs",
                approved=True
            )
            db.session.add(professional)
            db.session.commit()  # Commit after adding the professional
        return professional

def create_or_get_service_request(customer, service, professional):
    # Ensure we are within app context
    with app.app_context():
        # Ensure the customer, service, and professional are attached to the session
        if isinstance(customer, Customer) and not db.session.object_session(customer):
            customer = db.session.merge(customer)  # Attach the object to the session
        
        if isinstance(service, Service) and not db.session.object_session(service):
            service = db.session.merge(service)  # Attach the object to the session
        ServiceRequest
        if isinstance(professional, ServiceProfessional) and not db.session.object_session(professional):
            professional = db.session.merge(professional)  # Attach the object to the session

        # Query for an existing service request
        service_request = ServiceRequest.query.filter_by(
            customer_id=customer.id, service_id=service.id
        ).first()

        if not service_request:
            # If the service request doesn't exist, create a new one
            service_request = ServiceRequest(
                service_id=service.id,
                service_type_id=service.service_type_id,
                customer_id=customer.id,
                professional_id=professional.id,
                service_status="requested",
                remarks="Fix leaking pipe"
            )
            db.session.add(service_request)
            db.session.commit()  # Commit the session to save

        return service_request

from app import db, app
from models import Payment, PaymentStatus

def create_or_get_payment(service_request):
    with app.app_context():
        # Ensure the service_request is part of the session
        if not db.session.object_session(service_request):
            service_request = db.session.merge(service_request)  # Re-attach the service_request if detached
        
        # Query for an existing payment for the given service request
        payment = Payment.query.filter_by(request_id=service_request.id).first()

        if not payment:
            # If no payment exists, create a new payment
            payment = Payment(
                request_id=service_request.id,
                amount=500.0,  # You can dynamically set this value based on your business logic
                payment_status=PaymentStatus.PAID,
                payment_method="Credit Card"
            )
            db.session.add(payment)
            db.session.commit()  # Commit the session after adding the payment
        
        return payment


def create_or_get_feedback(service, customer, professional):
    with app.app_context():
        # Ensure service, customer, and professional are bound to the session
        if not db.session.object_session(service):
            service = db.session.merge(service)  # Re-attach service if detached

        if not db.session.object_session(customer):
            customer = db.session.merge(customer)  # Re-attach customer if detached

        if not db.session.object_session(professional):
            professional = db.session.merge(professional)  # Re-attach professional if detached

        # Handle service feedback
        service_feedback = Feedback.query.filter_by(
            service_id=service.id, customer_id=customer.id, type=FeedbackType.SERVICE).first()
        if not service_feedback:
            service_feedback = Feedback(
                service_id=service.id,
                customer_id=customer.id,
                type=FeedbackType.SERVICE,
                rating=5,
                comment="Great service, highly recommended!"
            )
            db.session.add(service_feedback)

        # Handle professional feedback
        professional_feedback = Feedback.query.filter_by(
            professional_id=professional.id, customer_id=customer.id, type=FeedbackType.PROFESSIONAL).first()
        if not professional_feedback:
            professional_feedback = Feedback(
                professional_id=professional.id,
                customer_id=customer.id,
                type=FeedbackType.PROFESSIONAL,
                rating=4,
                comment="Very professional and timely."
            )
            db.session.add(professional_feedback)

        # Commit after adding both feedback entries
        db.session.commit()

# Function to initialize the database
def initialize_db():
    with app.app_context():
        create_or_get_admin()
        customer = create_or_get_customer()
        service = create_or_get_service()
        professional = create_or_get_service_professional()
        service_request = create_or_get_service_request(customer, service, professional)
        create_or_get_payment(service_request)
        create_or_get_feedback(service, customer, professional)

# Function to reset the database
def reset_database():
    with app.app_context():
        db.drop_all()  # Drop all tables
        db.create_all()  # Recreate all tables
        db.session.commit()
