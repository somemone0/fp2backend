
from flask import request
from models import User, Post, Token
from jwt_util import getUserFromToken, validateToken
import jwt
import datetime

from flask import current_app as app
from app import db


@app.route("/", methods=["GET"])
def main():
    return "This is the backend, you shouldn't be seeing this."

@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]

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

    exp_date = datetime.datetime.now() + datetime.timedelta(days=2)
    token = Token(token=encoded_jwt, exp_date=exp_date)
    db.session.add(token)
    db.session.commit()

    result['result'] = "success"
    result['token'] = encoded_jwt

    return result

@app.route("/signup", methods=['POST'])
def signup():

    username = request.json['username']
    password = request.json['password']

    result = {}

    check_username = User.query.filter_by(username=username).first()
    if check_username is not None:
        result['result'] = "usernametaken"
        result['token'] = ""

        return result

    new_user = User(username=username, password=password, display_name=username)
    db.session.add(new_user)

    encoded_jwt = jwt.encode({"username": username, "password": password}, app.config["SECRET_KEY"], algorithm="HS256")

    exp_date = datetime.datetime.now() + datetime.timedelta(days=2)
    token = Token(token=str(encoded_jwt), exp_date=exp_date, exp=False)
    db.session.add(token)
    db.session.commit()

    result['result'] = 'success'
    result['token'] = encoded_jwt

    return result

@app.route("/logout", methods=["POST"])
def logout():
    token = request.json['token']

    checkToken = Token.query.filter_by(token=token).first()
    if checkToken is None:
        return "", 403
    
    checkToken.exp = True
    db.session.commit()
    
    return "", 200

@app.route("/post", methods=["POST"])
def post():
    content = request.json["content"]
    reply_to = request.json["reply_to"]
    token = request.json["token"]

    result = validateToken(token)
    if result == 1:
        return "", 403
    
    user = getUserFromToken(token)

    post = Post(content=content, user=user, date_created=datetime.datetime.now())

    if reply_to:
        reply_post = Post.query.filter_by(id=reply_to)
        if reply_post is None:
            return "", 404
        post.master_id = reply_post

    db.session.add(post)
    db.session.commit()

    return "", 200

@app.route("/like")
def like():
    post = request.json["post"]
    token = request.json["token"]

    result = validateToken(token)
    if result == 1:
        return "", 403
    
    user = getUserFromToken(token)

    if not post:
        return "", 400
    
    post_object = Post.query.get(int(post))
    post_object.likes.append( user )

    db.session.commit()
    return "", 200

@app.route("/addfollow")
def add_follow():
    user = request.json["user"]
    token = request.json["token"]

    result = validateToken(token)
    if result == 1:
        return "", 403
    
    following_user = getUserFromToken(token)

    user_object = User.query.filter_by(username=user).first()

    user_object.followers.append(following_user)
    db.session.commit()
    return "", 200

@app.route("/changebio", methods=['POST'])
def change_bio():
    bio = request.json["bio"]
    token = request.json["token"]

    result = validateToken(token)
    if result == 1:
        return "", 403
    
    following_user = getUserFromToken(token) 
    
    following_user.bio = bio
    db.session.commit()

    return "", 200
