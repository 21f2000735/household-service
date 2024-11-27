from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
from werkzeug.utils import secure_filename
from app import app,db
from models import Admin, Customer, ServiceProfessional , Service, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask import Flask, jsonify
from flask_swagger import swagger

from config import *


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
    
    return render_template(
        'admin/home.html',
        professionals=professionals,
        services=services,
        service_requests=service_requests
    )



@app.route('/customers/home')
def customers_home():
    return render_template('customers/home.html')







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



@app.route('/professionals/home')
def professionals_home():
    userId = session.get('userId')
    # Fetch data from the database
    professionals = ServiceProfessional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    
    return render_template(
        'professionals/home.html',
        professionals=professionals,
        services=services,
        service_requests=service_requests
    )
    


@app.route('/professionals/accept_request', methods=['POST'])
def accept_request():
    service_id = request.form['service_id']
    # Fetch the request and update its status
    service_request = Service.query.get_or_404(service_id)
    service_request.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('professional_home'))

@app.route('/professionals/reject_request', methods=['POST'])
def reject_request():
    service_id = request.form['service_id']
    # Fetch the request and update its status
    service_request = Service.query.get_or_404(service_id)
    service_request.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('professional_home'))

@app.route('/reset_db')
def reset_db():
    models.reset_database()  # Reset the database (drop and recreate tables)
    return "Database has been reset!"