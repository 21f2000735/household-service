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
from models import *

from config import *
todaydate = datetime.utcnow()

from flask import session, flash, redirect, url_for
from functools import wraps

def auth_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if 'admin_id' exists in session
        if 'userId' in session:
            # If authenticated, proceed to the original function
            return func(*args, **kwargs)
        else:
            # If not authenticated, redirect to login page
            flash("Please log in first.", "warning")
            return redirect(url_for('login_post'))
    return decorated_function




@app.route('/')
def index():
    return redirect(url_for('login')) 


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
    flash('Login with username or password')
    return redirect(url_for('login'))



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
@auth_required
def add_edit_service():
    # Get data from the form
    service_id = request.form['service_id']  # Get service_id, might be empty for a new service
    service_name = request.form['service_name']
    service_description = request.form['service_description']
    service_base_price = request.form['base_price']
    service_time_required = request.form['time_required']
    service_type_id = request.form['service_type_id'] #holds id

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
                time_required=service_time_required,
                service_type_id=service_type_id
            )
        db.session.add(service)

        
        db.session.commit()
        return redirect(url_for('admin_home')) 
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500
    

@app.route('/admin/delete_service/<int:service_id>', methods=['POST'])
@auth_required
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

def enrich_services(services):
    enriched_services = []
     

    for service in services:
        service_type_name = ServiceType.get_by_id(service.service_type_id).display_name
        
        enriched_service = {
            'id': service.id,
            'name': service.name,
            'base_price': service.base_price,
            'time_required': service.time_required,
            'description': service.description[:15] + '...' if service.description and len(service.description) > 15 else service.description,
            'service_type_name': service_type_name,
        }

        enriched_services.append(enriched_service)

    return enriched_services

def enrich_service_requests(service_requests, customer, mappings, professional=None):
    """
    Enrich service requests with additional details for rendering.
    If the customer is None, fetch the customer from the database.
    """
    enriched_requests = []
 
    for request in service_requests:
        # If customer is None, fetch from the database
        
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
        service_type_name = (
        ServiceType.get_by_id(request.service_type_id).display_name
        if ServiceType.get_by_id(request.service_type_id)
        else 'Service Type Not Found'
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
        print(request.service_type_id)
        print(service_type_name)
        enriched_request = {
            'id': request.id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'customer_pincode': customer_pincode,
            'service_request_rating': request.rating or 'N/A',
            'professional_name': professional_name,
            'professional_phone': professional_phone,
            'service_name': request.service_name,
            'service_type_name': service_type_name,
            'date_of_request': date_of_request,
            'date_of_completion': date_of_completion,
            'status': request.service_status or 'N/A',
            'remarks': request.remarks or 'N/A',
            'service_type_id': request.service_type_id
            }
        
        # If a professional parameter is provided, add professional details
        if professional:
            enriched_request['professional'] = {
                'name': professional.name,
                'phone': professional.phone,
                'email': professional.email,  # You can add more attributes as needed
            }
        
        enriched_requests.append(enriched_request)
       
    print(enriched_requests)
    return enriched_requests




################################ Customer API Start ##############

@app.route('/customers/home')
@auth_required
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
@auth_required
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
@auth_required
def new_service_request():
    try:
        # Fetch customer info from the session
        #validate_csrf_token()
        service_id = request.form.get('service_id')
        service_name = request.form.get('service_name')
        service_type_id = request.form.get('service_type_id')
        request_date = request.form.get('request_date')
        remark = request.form.get('remark', '')  # Optional field
        payment_option = request.form.get('payment_option')
        customer = Customer.query.filter_by(id=session['userId']).first()
        # Fetch all service requests (could be filtered if needed)
        service_requests = ServiceRequest.query.all()
        print(service_id)
        print(service_name)
        print(request_date)
        if service_id: 
            service = Service.query.get_or_404(service_id)
            service_request = ServiceRequest(
                service_id=service.id,
                service_name=service_name,
                customer_id=customer.id,
                service_status=ServiceRequestStatus.REQUESTED.display_name,
                remarks=remark,
                service_type_id=service_type_id,
                date_of_request=  datetime.strptime(request_date, '%Y-%m-%d')
            )
            db.session.add(service_request)
            db.session.commit()

        return redirect(url_for('customers_home'))    
       
    except Exception as e:
        # Handle any errors that occur during the process
        return f"An error occurred: {e}", 500


@app.route('/customers/services')
@auth_required
def customer_services():
 # Fetch all service requests for this customer
      # Create mappings for IDs to their objects
        mappings = create_id_mappings()

      
        return render_template(
            'customer_services.html',
            service_types=ServiceType.list_all(),
            services=Service.query.all(),
            service_type_mapping=mappings['service_type_mapping'],
            customer_mapping=mappings['customer_mapping'],
            professional_mapping=mappings['professional_mapping']
        )

@app.route('/customers/services/action', methods=['POST'])
@auth_required
def customer_services_action():
       
    request_id = request.form.get('request_id')
    service_date_str = request.form.get('service_date')
    rating = request.form.get('rating')
    remarks = request.form.get('remarks')

    # Convert service_date to datetime format
    service_date = datetime.strptime(service_date_str, '%Y-%m-%d') if service_date_str else None

    # Find the service request by ID (you can adjust this based on your database structure)
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404

    # Update service request details
    print(service_date)
    service_request.date_of_request = service_date
    service_request.rating = rating
    service_request.remarks = remarks

    # Save changes to the database
    db.session.commit()
    return redirect(url_for('customers_home'))

################################ Customer API End##############

################################ Professional  API Start ##############

@app.route('/professionals/home')
@auth_required
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
        print(today_service_requests)

        return render_template(
            'professionals/home.html',
            service_professional=service_professional,
            today_service_requests=enriched_today_requests,
            past_service_requests=enriched_past_requests
        )
    except Exception as e:
        return f"An error occurred while loading professional home: {e}", 500


@app.route('/professionals/service_request/<int:service_request_id>/<action>', methods=['POST'])
@auth_required
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
            service_request.professional_id = session['userId']
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
@auth_required
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
@auth_required
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


@app.route('/admin/summary')
@auth_required
def admin_summary():
    # Fetch data from the database (replace with real queries)
    professionals = ServiceProfessional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    enriched_service_requests = enrich_service_requests(service_requests, None, create_id_mappings())
    services_new = enrich_services(services)
    
    # Prepare the data for the bar chart (Service Requests Overview)
    service_request_counts = {
    'pending': len([req for req in enriched_service_requests if req['status'] == 'requested']),
    'in_progress': len([req for req in enriched_service_requests if req['status'] == 'assigned']),
    'completed': len([req for req in enriched_service_requests if req['status'] == 'closed'])
}

    # Prepare data for the circle chart (Rating Distribution)
    ratings = Feedback.query.all()
    rating_distribution = {
        'excellent': sum(1 for feedback in ratings if feedback.rating == 5),
        'good': sum(1 for feedback in ratings if feedback.rating == 4),
        'average': sum(1 for feedback in ratings if feedback.rating == 3),
        'poor': sum(1 for feedback in ratings if feedback.rating <= 2)
    }

    return render_template(
        'admin/summary.html',
        professionals=professionals,
        services=services_new,
        service_requests=enriched_service_requests,
        service_types=ServiceType.list_all(),
        service_request_counts=service_request_counts,
        rating_distribution=rating_distribution
    )


@app.route('/admin/home')
@auth_required
def admin_home():
    # Fetch data from the database
    professionals = ServiceProfessional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    enriched_service_requests = enrich_service_requests(service_requests, None, create_id_mappings())
    services_new= enrich_services(services)
    
    return render_template(
        'admin/home.html',
        professionals=professionals,
        services=services_new,
        service_requests=enriched_service_requests,
        service_types=ServiceType.list_all(),
    )


@app.route('/admin/services')
@auth_required
def admin_services():
    # Replace with your logic to fetch service data and render the template
    # Fetch all service requests for this customer
      # Create mappings for IDs to their objects
        mappings = create_id_mappings()

      
        return render_template(
            'admin_services.html',
            service_types=ServiceType.list_all(),
            services=Service.query.all(),
            service_type_mapping=mappings['service_type_mapping'],
            customer_mapping=mappings['customer_mapping'],
            professional_mapping=mappings['professional_mapping']
        )

################ Admin End ##########
@app.route('/logout')
def logout():
    # Remove all session data
    session.pop('userId', None)
    session.pop('role', None)

    flash("You have been logged out successfully.", "success")
    return redirect(url_for('home'))

@app.route('/register_customer', methods=['GET'])
def register_customer():
    return render_template('register_customer.html')

@app.route('/register_customer', methods=['POST'])
def register_customer_post():
        name = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        password = request.form.get('password')

        # Hash the password for security
        password_hash = generate_password_hash(password)

        # Save the customer to the database
        try:
            new_customer = Customer(
                name=name,
                username=name,
                email=email,
                phone=phone,
                address=address,
                pincode=pincode,
                password_hash=password_hash
            )
            db.session.add(new_customer)
            db.session.commit()
            flash('Customer registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return render_template('register_customer.html', service_types=ServiceType)


@app.route('/register_professional', methods=['GET'])
def register_professional():
    return render_template('register_professional.html', service_types=ServiceType)

@app.route('/register_professional', methods=['POST'])
def register_professional_post():
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    experience = request.form.get('experience')
    description = request.form.get('description')
    service_type = request.form.get('serviceType')
    password = request.form.get('password')
    
        # Hash the password for security
    password_hash = generate_password_hash(password)

        # Save the professional to the database
    try:
            new_professional = ServiceProfessional(
                username=username,
                name=username,
                email=email,
                phone=phone,
                experience=int(experience) if experience else None,
                description=description,
                service_type_id=service_type,  # ServiceType Enum field
                password_hash=password_hash,
                approved=True
            )
            db.session.add(new_professional)
            db.session.commit()
            flash('Professional registration successful!', 'success')
            return redirect(url_for('login'))
    except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    # Pass service types to the template
    return render_template('register_professional.html', service_types=ServiceType)



##
@app.route('/professional/services')
@auth_required
def professional_services():
    # Replace with your logic to fetch service data and render the template
    # Fetch all service requests for this customer
      # Create mappings for IDs to their objects
        mappings = create_id_mappings()

      
        return render_template(
            'prof_services.html',
            service_types=ServiceType.list_all()
        )