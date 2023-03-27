from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from descope import DescopeClient, DeliveryMethod, AuthException
import requests

auth = Blueprint('auth', __name__)
descope_client = DescopeClient(project_id="P2MzaPz4LUiqdwSPOYJ170UHYcE5")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Sucessfully logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password was not correct, try again.', category='error')
        else:
            flash('User does not exist, please sign-up first.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/login/google', methods=['GET'])
def google_login():
    provider = "google"
    redirect_url = "http://127.0.0.1:5000/login/token_exchange"
        
    try:
        resp = descope_client.oauth.start(provider=provider, return_url=redirect_url)
        print ("Successfully started Oauth flow")
        if not resp:
            flash('There was an issue with the Google OAuth provider redirect.', category='error')
        else:
            return redirect(resp['url'])
    except AuthException as error:
        print ("Failed to start Oauth flow")
        print ("Status Code: " + str(error.status_code))
        print ("Error: " + str(error.error_message))

    return render_template("login.html", user=current_user)

@auth.route('/login/token_exchange', methods=['GET'])
def token_exchange():
    code = request.args.get('code')
    try:
        resp = descope_client.oauth.exchange_token(code=code)
        print ("Successfully Finished Oauth flow")
        
        email = resp['user']['email']
        user = User.query.filter_by(email=email).first()
        if user:
            print(user.email)
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    except AuthException as error:
        print ("Failed to finish Oauth flow")
        print ("Status Code: " + str(error.status_code))
        print ("Error: " + str(error.error_message))

    return redirect(url_for('auth.login'))

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    
    try:
        resp = descope_client.logout(refresh_token)
        print ("Successfully logged user out of current session.")
    except AuthException as error:
        print ("Failed to log user out of current session.")
        print ("Status Code: " + str(error.status_code))
        print ("Error: " + str(error.error_message))
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already is registered, please log in instead.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.home')) # or you could use '/'

    return render_template("register.html", user=current_user)