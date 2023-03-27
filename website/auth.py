from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, current_user
from descope import DescopeClient, AuthException

auth = Blueprint('auth', __name__)
descope_client = DescopeClient(project_id="P2MzaPz4LUiqdwSPOYJ170UHYcE5")

SUPPORTED_PROVIDERS = ['google', 'facebook']

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Cannot use Descope Flows with password auth
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


@auth.route('/login/<string:provider>', methods=['GET'])
def google_login(provider):
    if provider in SUPPORTED_PROVIDERS:
        redirect_url = request.url_root + url_for('auth.token_exchange')
        print(redirect_url)
        
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
        
        # Validate user, if not present, add to DB
        email = resp['user']['email']
        user = User.query.filter_by(email=email).first()
        login_user(user, remember=True)
        return redirect(url_for('views.home'))
    except AuthException as error:
        print ("Failed to finish Oauth flow")
        print ("Status Code: " + str(error.status_code))
        print ("Error: " + str(error.error_message))

    return redirect(url_for('auth.login'))


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    if request.args.get("refresh-token"):
        try:
            resp = descope_client.logout(request.args.get("refresh-token"))
            print("Successfully logged user out of current session.")
            print(resp)
        except AuthException as error:
            print("Failed to log user out of current session.")
            print("Status Code: " + str(error.status_code))
            print("Error: " + str(error.error_message))
    else:
        logout_user()

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
            new_user_json = {
                "name": firstName,
                "email": email,
            }
            jwt_response = descope_client.password.sign_up(login_id=email, password=password1, user=new_user_json)
            print(jwt_response)
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='sha256'))
            createNewUser(new_user)

    return render_template("register.html", user=current_user)

def createNewUser(user):
    db.session.add(user)
    db.session.commit()
    flash('Account created!', category='success')
    return redirect(url_for('views.home'))