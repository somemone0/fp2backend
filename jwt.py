from app import app
from models import User
import jwt

def getUserFromToken(token):
    decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithm="HS256")

    if decoded["username"] is not None:
        user = User.query.filter_by(username=decoded["username"])
        if user is not None:
            return user
        
    return None

def validateToken(token):
    checkToken = Token.query.get(token)
    if checkToken is None:
        return 1
    
    if checkToken.exp_date < datetime.datetime.now:
        checkToken.exp = True
        db.session.commit()
    
    if checkToken.exp:
        return 1
    
    return checkToken