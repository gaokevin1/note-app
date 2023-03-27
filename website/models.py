from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import request, jsonify, make_response
from functools import wraps
from descope import DescopeClient
from http.cookies import SimpleCookie

descope_client = DescopeClient(project_id='P2MzaPz4LUiqdwSPOYJ170UHYcE5')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')


# token decorator 
def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        cookie = SimpleCookie()
        # ensure the jwt-token is passed with the headers
        if 'Cookie' in request.headers:
            cookie_response = request.headers['Cookie']
            cookie.load(cookie_response)
            cookies = {k: v.value for k, v in cookie.items()}
            print(cookies)
        if not cookies: 
            return make_response(jsonify({"message": "A valid cookie is missing!"}), 401)
        try:
            jwt_response = descope_client.validate_session(session_token=cookies['session'])
            print ("Successfully validated user session:")
            print (jwt_response)
            
        except Exception as error:
            print ("Could not validate user session. Error:")
            print (error)
            return make_response(jsonify({"message": "Invalid token!"}), 401)
         # Return the user information attached to the token
        return f(current_user, *args, **kwargs)
    return decorator