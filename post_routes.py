from app import app, db
from Flask import request
from models import User, Post, Token
from jwt import getUserFromToken, validateToken
import jwt
import datetime

@app.route("/", methods=["GET"])
def main():
    return "This is the backend, you shouldn't be seeing this."

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    result = {}
    user_object = User.query.filter_by(username=username).first()
    if user_object is None:
        result['result'] = "badusername"
        result['token'] = ""
        return result
    
    if user_object.password is not password:
        result['result'] = "badpassword"
        result['token'] = ""
        return result
    
    encoded_jwt = jwt.encode({"username": username, "password": password}, app.config["SECRET_KEY"], algorithm="HS256")

    exp_date = datetime.datetime.now + datetime.timedelta(days=2)
    token = Token(token=encoded_jwt, exp_date=exp_date, user=user_object)

    result['result'] = "success"
    result['token'] = encoded_jwt

    return result

@app.route("/signup", methods=['POST'])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")

    result = {}

    check_username = User.query.filter_by(username=username).first()
    if check_username is not None:
        result['result'] = "usernametaken"
        result['token'] = ""

        return result

    new_user = User(username=username, password=password, display_name=username)
    db.session.add(new_user)
    db.session.commit()

@app.route("/logout", methods=["POST"])
def logout():
    token = request.form.get("token")

    checkToken = Token.query.filter_by(token=token).first()
    if checkToken is None:
        return 1
    
    checkToken.exp = True
    db.session.commit()
    
    return 0

@app.route("/post", methods=["POST"])
def post():
    content = request.form.get("content")
    reply_to = request.form.get("reply_to")
    token = request.form.get("token")

    result = validateToken(token)
    if result == 1:
        return 1
    
    user = getUserFromToken(token)

    post = Post(content=content, user=user, date_created=datetime.datetime.now())

    if reply_to:
        reply_post = Post.query.filter_by(id=reply_to)
        if reply_post is None:
            return 2
        post.master_id = reply_post

    db.session.add(post)
    db.session.commit()

    return 0

@app.route("/like")
def like():
    post = request.form.get("post")
    token = request.form.get("token")

    result = validateToken(token)
    if result == 1:
        return 1
    
    user = getUserFromToken(token)

    if not post:
        return 2
    
    post_object = Post.query.get(int(post))
    post_object.likes.append( user )

    db.session.commit()
    return 0

@app.route("/addfollow")
def add_follow():
    user = request.form.get("user")
    token = request.form.get("token")

    result = validateToken(token)
    if result == 1:
        return 1
    
    following_user = getUserFromToken(token)

    user_object = User.query.filter_by(user=user).first()

    user_object.friends.append(following_user)
    db.session.commit()
    return 0

@app.route("/changebio")
def change_bio():
    bio = request.form.get("bio")
    token = request.form.get("token")

    result = validateToken(token)
    if result == 1:
        return 1
    
    following_user = getUserFromToken(token) 
    
    following_user.bio = bio
    db.session.commit()

    return 0
