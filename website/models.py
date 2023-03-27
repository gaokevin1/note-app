from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import request, jsonify, make_response
from functools import wraps
from descope import DescopeClient
import requests

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
        try:
            session = requests.Session()
            response = session.get(request.url_root)
            print(session.cookies.get_dict())

            jwt_response = descope_client.validate_session(session_token=session.cookies['session'])
            print ("Successfully validated user session:")
            print (jwt_response)
            return f({"session_active": True, "jwt": jwt_response, "descope_login": True}, *args, **kwargs)
        except Exception as error:
            print ("Could not validate user session. Error:")
            print (error)
        
        return f({"session_active": False, "jwt": 0}, *args, **kwargs)
    return decorator