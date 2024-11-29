from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
from werkzeug.utils import secure_filename
from app import app,db
from models import Admin, Customer, ServiceProfessional , Service, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask import Flask, jsonify
from flask_swagger import swagger
from enums import ServiceType, ServiceRequestStatus
from sqlalchemy import or_, and_

from config import *
todaydate = datetime.utcnow()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('email')
    password = request.form.get('password')
    print(username)
    print(password)

    if not username or not password:
        flash('All the fields are required')
        return redirect(url_for('login'))

    # Check if the user is an Admin
    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password_hash, password):
        session['userId'] = admin.id
        session['role'] = 'admin'
        return redirect(url_for('admin_home'))

    # Check if the user is a Customer
    customer = Customer.query.filter_by(username=username).first()
    if customer and check_password_hash(customer.password_hash, password):
        session['userId'] = customer.id
        session['role'] = 'customer'
        return redirect(url_for('customers_home'))

    # Check if the user is a Service Professional
    professional = ServiceProfessional.query.filter_by(username=username).first()
    if professional and check_password_hash(professional.password_hash, password):
        session['userId'] = professional.id
        session['role'] = 'professional'
        return redirect(url_for('professionals_home'))

    # If no user found or password is incorrect
    flash('Invalid username or password')
    return redirect(url_for('login'))


@app.route('/admin/home')
def admin_home():
    # Fetch data from the database
    professionals = ServiceProfessional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    enriched_service_requests = enrich_service_requests(service_requests, None, create_id_mappings())
    
    return render_template(
        'admin/home.html',
        professionals=professionals,
        services=services,
        service_requests=enriched_service_requests
    )

def create_id_mappings():
    # Assuming `ServiceType`, `Customer`, `Professional` are your models
    service_type_mapping = {st.id: st for st in ServiceType}
    customer_mapping = {c.id: c for c in Customer.query.all()}
    professional_mapping = {p.id: p for p in ServiceProfessional.query.all()}
    return {
        'service_type_mapping': service_type_mapping,
        'customer_mapping': customer_mapping,
        'professional_mapping': professional_mapping
    }







@app.route('/admin/add_edit_service', methods=['POST'])
def add_edit_service():
    # Get data from the form
    service_id = request.form['service_id']  # Get service_id, might be empty for a new service
    service_name = request.form['service_name']
    service_description = request.form['service_description']
    service_base_price = request.form['base_price']
    service_time_required = request.form['time_required']
    print(service_id)
    print(service_name)
    print(service_description)

    try:
        if service_id: 
            service = Service.query.get_or_404(service_id)
            service.name = service_name
            service.description = service_description
            service.base_price = float(service_base_price)
            service.time_required = service_time_required
        else:  
            service = Service(
                name=service_name,
                description=service_description,
                base_price=float(service_base_price),
                time_required=service_time_required
            )
        db.session.add(service)

        
        db.session.commit()
        return redirect(url_for('admin_home')) 
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500
    

@app.route('/admin/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    try:
        print(service_id)
        service = Service.query.get_or_404(service_id)

        db.session.delete(service)
        db.session.commit()

        return redirect(url_for('admin_home'))  
    except Exception as e:
        db.session.rollback()
        return f"An error occurred while deleting the service: {e}", 500




@app.route('/reset_db')
def reset_db():
    models.reset_database()  # Reset the database (drop and recreate tables)
    return "Database has been reset!"


################################ Common Methods ##############


def enrich_service_requests(service_requests, customer, mappings, professional=None):
    """
    Enrich service requests with additional details for rendering.
    If the customer is None, fetch the customer from the database.
    """
    enriched_requests = []
    
    for request in service_requests:
        # If customer is None, fetch from the database
        if customer is None:
            customer = Customer.query.get(request.customer_id)  # Fetch customer from the database

        # Fetch professional details
        professional_name = (
            mappings['professional_mapping'][request.professional_id].name
            if request.professional_id and request.professional_id in mappings['professional_mapping']
            else 'Professional Not Assigned'
        )
        professional_phone = (
            mappings['professional_mapping'][request.professional_id].phone
            if request.professional_id and request.professional_id in mappings['professional_mapping']
            else 'N/A'
        )
        service_name = (
            mappings['service_type_mapping'][request.service_id].name
            if request.service_id in mappings['service_type_mapping']
            else 'Service Not Found'
        )
        
        # Fetch customer details
        customer_name = customer.name if customer else 'N/A'
        customer_phone = customer.phone if customer and customer.phone else 'N/A'
        customer_address = customer.address if customer and customer.address else 'N/A'
        customer_pincode = customer.pincode if customer and customer.pincode else 'N/A'

        date_of_request = request.date_of_request if request.date_of_request else 'N/A'
        date_of_completion = request.date_of_completion if request.date_of_completion else 'N/A'

        if (request.rejected_by_professional_id is not None and
            professional is not None and
            request.rejected_by_professional_id == professional.id):
            continue  # Skip this request
    
        enriched_request = {
            'id': request.id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'customer_pincode': customer_pincode,
            'service_request_rating': request.rating or 'N/A',
            'professional_name': professional_name,
            'professional_phone': professional_phone,
            'service_name': service_name,
            'date_of_request': date_of_request,
            'date_of_completion': date_of_completion,
            'status': request.service_status or 'N/A',
            'remarks': request.remarks or 'N/A'
        }
        
        # If a professional parameter is provided, add professional details
        if professional:
            enriched_request['professional'] = {
                'name': professional.name,
                'phone': professional.phone,
                'email': professional.email,  # You can add more attributes as needed
            }
        
        enriched_requests.append(enriched_request)
    
    return enriched_requests




################################ Customer API Start ##############

@app.route('/customers/home')
def customers_home():
    try:
        # Create mappings for IDs to their objects
        mappings = create_id_mappings()

        # Get the current logged-in customer
        customer = Customer.query.filter_by(id=session['userId']).first()
        if not customer:
            return "Customer not found", 404

        # Fetch all service requests for this customer
        service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()

        # Enrich service requests using the helper function
        enriched_service_requests = enrich_service_requests(service_requests, customer, mappings)

        return render_template(
            'customers/home.html',
            customer=customer,
            service_requests=enriched_service_requests,
            service_types=ServiceType.list_all(),
            services=Service.query.all(),
            service_type_mapping=mappings['service_type_mapping'],
            customer_mapping=mappings['customer_mapping'],
            professional_mapping=mappings['professional_mapping']
        )
    except Exception as e:
        return f"An error occurred while loading customer home: {e}", 500


@app.route('/customers/best_package/<int:service_type_id>', methods=['POST'])
def view_package(service_type_id):
    try:
        # Get the current logged-in customer
        customer = Customer.query.filter_by(id=session['userId']).first()
        if not customer:
            return "Customer not found", 404

        # Fetch services for the given service type
        services = (
            Service.query.filter_by(service_type_id=service_type_id).all()
            if service_type_id
            else Service.query.all()
        )

        # Fetch all service requests for the customer
        service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()

        # Enrich service requests using the helper function
        enriched_service_requests = enrich_service_requests(service_requests, customer, create_id_mappings())

        return render_template(
            'customers/home_best_package.html',
            service_type=next(
                (stype for stype in ServiceType.list_all() if stype.id == service_type_id), None
            ),
            customer=customer,
            services=services,
            service_requests=enriched_service_requests
        )
    except Exception as e:
        return f"An error occurred while loading the best package view: {e}", 500


@app.route('/customers/new_service_request/', methods=['POST'])
def new_service_request():
    try:
        # Fetch customer info from the session
        #validate_csrf_token()
        service_id = request.form.get('service_id')
        remark = request.form.get('remark', '')  # Optional field
        payment_option = request.form.get('payment_option')
        customer = Customer.query.filter_by(id=session['userId']).first()
        # Fetch all service requests (could be filtered if needed)
        service_requests = ServiceRequest.query.all()
        print(service_id)
        if service_id: 
            service = Service.query.get_or_404(service_id)
            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.id,
                service_status="requested",
                remarks=remark
            )
            print(service_request)
            db.session.add(service_request)
            db.session.commit()

        return redirect(url_for('customers_home'))    
       
    except Exception as e:
        # Handle any errors that occur during the process
        return f"An error occurred: {e}", 500


################################ Customer API End##############

################################ Professional  API Start ##############

@app.route('/professionals/home')
def professionals_home():
    try:
        # Get the current logged-in professional
        service_professional = ServiceProfessional.query.filter_by(id=session['userId']).first()
        if not service_professional:
            return "Professional not found", 404

        # Today's service requests: requests that are requested but not yet assigned to a professional
        today_service_requests = ServiceRequest.query.filter(
        or_(
        # Condition 1: Unassigned and status is 'Requested'
        and_(
            ServiceRequest.professional_id == None,
            ServiceRequest.service_status == ServiceRequestStatus.REQUESTED.display_name
        ),
        # Condition 2: Assigned to the current professional and status is 'Assigned'
        and_(
            ServiceRequest.professional_id == service_professional.id,
            ServiceRequest.service_status == ServiceRequestStatus.ASSIGNED.display_name
        )
        )
        ).all()

        closed_service_requests = ServiceRequest.query.filter(
        and_(
            ServiceRequest.professional_id == service_professional.id,
            ServiceRequest.service_status == ServiceRequestStatus.CLOSED.display_name
        )
        ).all()
        # Enrich service requests using the helper function
        mappings = create_id_mappings()
        enriched_today_requests = enrich_service_requests(today_service_requests,None, mappings,service_professional)
        enriched_past_requests = enrich_service_requests(closed_service_requests, None, mappings,service_professional)

        return render_template(
            'professionals/home.html',
            service_professional=service_professional,
            today_service_requests=enriched_today_requests,
            past_service_requests=enriched_past_requests
        )
    except Exception as e:
        return f"An error occurred while loading professional home: {e}", 500


@app.route('/professionals/service_request/<int:service_request_id>/<action>', methods=['POST'])
def service_request_action(service_request_id, action):
    # Fetch the service request from the database
    service_request = ServiceRequest.query.get_or_404(service_request_id)


    # Handle actions based on the action parameter
    if action == 'accept':
        if service_request.service_status == ServiceRequestStatus.REQUESTED.display_name:  # Only accept if the request is in 'Requested' state
            service_request.service_status = ServiceRequestStatus.ASSIGNED.display_name
            service_request.professional_id = session['userId']
        else:
            flash("Request cannot be accepted. It is not in the 'Requested' state.", "error")
            return redirect(url_for('professionals_home'))

    elif action == 'reject':
        if service_request.service_status == ServiceRequestStatus.REQUESTED.display_name:  # Only reject if the request is in 'Requested' state
            service_request.service_status = ServiceRequestStatus.REQUESTED.display_name
            service_request.rejected_by_professional_id = session['userId']
        else:
            flash("Request cannot be rejected. It is not in the 'Requested' state.", "error")
            return redirect(url_for('professionals_home'))

    elif action == 'close':
        if service_request.service_status == ServiceRequestStatus.ASSIGNED.display_name:  # Only close if the request is in 'Assigned' state
            service_request.service_status = ServiceRequestStatus.CLOSED.display_name
            service_request.professional_id = session['userId']
            service_request.date_of_completion = todaydate
        else:
            flash("Request cannot be closed. It is not in the 'Assigned' state.", "error")
            return redirect(url_for('professionals_home'))

    else:
        flash("Invalid action.", "error")
        return redirect(url_for('professionals_home'))

    # Commit the changes to the database
    db.session.commit()

    # Return to the home page with the updated service requests
    return redirect(url_for('professionals_home'))


################### Professional End point End ############# 
################### Amdin Start###############
@app.route('/professionals/action', methods=['POST'])
def handle_professional_action():
    from flask import flash

    def process_action(professional, action):
        """Process the given action on the professional."""
        if action == 'approve':
            professional.approved = True
            return f"Professional {professional.name} approved successfully.", "success"
        elif action == 'reject':
            professional.approved = False
            return f"Professional {professional.name} rejected successfully.", "warning"
        elif action == 'delete':
            db.session.delete(professional)
            return f"Professional {professional.name} deleted successfully.", "danger"
        else:
            return "Invalid action. No changes were made.", "error"

    # Get the form data
    professional_id = request.form.get('professional_id')
    action = request.form.get('action')

    # Find the professional in the database
    professional = ServiceProfessional.query.filter_by(id=professional_id).first()

    if not professional:
        flash(f"Professional with ID {professional_id} not found.", "error")
        return redirect(url_for('admin_home'))

    try:
        # Process the action and get a message
        message, category = process_action(professional, action)
        db.session.commit()  # Commit changes to the database
        flash(message, category)

    except Exception as e:
        db.session.rollback()  # Rollback transaction on error
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for('admin_home'))

###########
@app.route('/service_requests/update_status', methods=['POST'])
def update_status():
    request_id = request.form.get('request_id')
    new_status = request.form.get('status')

    # Validate and update the status (ensure the new status is valid)
    if new_status not in ['requested', 'assigned', 'closed']:
        return "Invalid status", 400  # You can handle this error more gracefully

    try:
        # Retrieve the request from the database (assuming `ServiceRequest` is your model)
        service_request = ServiceRequest.query.get(request_id)
        print(service_request)
        print(service_request.service_status)
        print(new_status)

        if service_request:
            # Update the status
            service_request.service_status = new_status

            # Commit the changes to the database
            db.session.commit()

            # Redirect to the page with a success message (optional)
            return redirect(url_for('admin_home')) # Assuming this is your view for the list
        else:
            return "Service Request not found", 404  # Handle case if request ID doesn't exist
    except Exception as e:
        return f"An error occurred: {e}", 500









################ Admin End##########

from flask import request, abort

def validate_csrf_token():
    token = session.get('_csrf_token', None)
    if not token or token != request.form.get('csrf_token'):
        abort(403)  # Forbidden