# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from flask import current_app as app
from app import db, login_manager
from app.base import blueprint  
from app.base.forms import LoginForm, CreateAccountForm,ChangePasswordForm,ResetPasswordForm
from app.base.models import User
from app.base.util import verify_pass,hash_pass,send_email
import re


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg=app.config['E0030'], form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)

    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]
        password     = request.form['password']

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Validate password
        if len(password) < 8:
            return render_template( 'accounts/register.html', 
                                    msg='Make sure your password is at lest 8 letters',
                                    success=False,
                                    form=create_account_form)
        elif re.search('[0-9]',password) is None:
            return render_template( 'accounts/register.html', 
                                    msg='MMake sure your password has a number in it',
                                    success=False,
                                    form=create_account_form)            
        elif re.search('[A-Z]',password) is None: 
            return render_template( 'accounts/register.html', 
                                    msg='Make sure your password has a capital letter in it',
                                    success=False,
                                    form=create_account_form)            
        elif re.search("[_@$]", password) is None: 
            return render_template( 'accounts/register.html', 
                                    msg='Make sure your password has a special symbol [ _ @  character in it',
                                    success=False,
                                    form=create_account_form)                           
        
        if not bool(request.form.getlist('agreeTerms')):
            return render_template( 'accounts/register.html', 
                                    msg='Please check agree to terms.',
                                    success=False,
                                    form=create_account_form)                                                 

        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?" 
        match = re.search(pattern, email)
        if not match:
            return render_template( 'accounts/register.html', 
                                    msg='Please enter valid email ',
                                    success=False,
                                    form=create_account_form)            

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()
        
        send_account_activation_email(user.email)

        return render_template( 'accounts/register.html', 
                                msg='an activation link is sent to ' + user.email, 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)

@blueprint.route('/changepassword', methods=['GET', 'POST'])
def change_password():
    change_password_form = ChangePasswordForm()

    if request.method == 'POST':
        if change_password_form.validate_on_submit():

            if change_password_form.password1.data != change_password_form.password2.data:
                return render_template( 'accounts/changepassword.html', msg='Passwords does not match.', form=change_password_form)
            else:
                user = current_user
                user.password = hash_pass(change_password_form.password1.data)
                db.session.add(user)
                db.session.commit()        
                return render_template( 'accounts/changepassword.html', msg='Passwords Updated Successfully.', form=change_password_form)
    else:
        return render_template( 'accounts/changepassword.html', form=change_password_form)

@blueprint.route('/reset', methods=['GET', 'POST'])
def reset():
    reset_form = ResetPasswordForm()
    if reset_form.validate_on_submit():
        try:
            user = User.query.filter_by(email=reset_form.email.data).first_or_404()
            send_password_reset_email(user.email)
            return render_template( 'accounts/resetpassword.html', 
                                        msg='an email is sent to '+user.email+' with instructions on reset', 
                                        success=True,
                                        form=reset_form)
        except Exception as error:
            if error.code == 404:
                return render_template( 'accounts/resetpassword.html',
                                        msg='Invalid email address!.', 
                                        success=False,
                                        form=reset_form)
            else: 
                return render_template( 'accounts/resetpassword.html', 
                                        msg='Problem processing request!.', 
                                        success=False,
                                        form=reset_form)

    return render_template('accounts/resetpassword.html', 
                                        success=False,
                                        form=reset_form)

def send_password_reset_email(user_email):
    send_email('Password Reset Request',user_email)

def send_account_activation_email(user_email):
    send_email('Account Activation Mail',user_email)    

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
