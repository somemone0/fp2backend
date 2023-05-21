
from models import User, Token
import datetime
from app import db
from flask import current_app as app
import jwt

def getUserFromToken(token):
    decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])

    if decoded["username"] is not None:
        user = User.query.filter_by(username=decoded["username"]).first()
        if user is not None:
            return user
        
    return None

def validateToken(token):
    checkToken = Token.query.filter_by(token=token).first()
    if checkToken is None:
        return 1
    
    if checkToken.exp_date < datetime.datetime.now():
        checkToken.exp = True
        db.session.commit()
    
    if checkToken.exp:
        return 1
    
    return checkToken