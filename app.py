from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
import sqlalchemy_serializer

db = SQLAlchemy()
app = Flask(__name__)

def wipe_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = ".&b..M1bU8/<r21#@fo90c"

db.init_app(app)

from models import User, Post, Token
from jwt_util import getUserFromToken, validateToken

@app.route("/", methods=["GET"])
def main():
    post = Post.query.get(1)
    user = User.query.get(1)

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

    if user_object.password != password:
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
    reply_to = request.json.get("reply_to")
    token = request.json["token"]

    result = validateToken(token)
    if result == 1:
        return "", 403
    
    user = getUserFromToken(token)

    post = Post(content=content, user=user, date_created=datetime.datetime.now())

    if reply_to:
        reply_post = Post.query.get(int(reply_to))
        if reply_post is None:
            return "", 404
        post.master_id = reply_post.id

    db.session.add(post)
    db.session.commit()

    return "", 200

@app.route("/like", methods=["POST"])
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

@app.route("/addfollow", methods=['POST'])
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

@app.route("/posts", methods=["GET"])
def posts():
    by = request.args.get("by")
    likedBy = request.args.get("likedBy")
    id = request.args.get("id")
    madeAfter = request.args.get("madeAfter")
    replyTo = request.args.get("replyTo")

    if id:
        return [Post.query.get(id).as_dict()]
    
    posts = Post.query.all()

    if by:
        new_posts = []
        for post in posts:
            if post.user.username == by:
                new_posts.append(post.as_dict())
        
        posts = new_posts
    
    if likedBy:
        new_posts = []
        for post in posts:
            if post.likes.contains(likedBy):
                new_posts.append(post.as_dict())
        
        posts = new_posts
    
    if replyTo:
        new_posts = []
        for post in posts:
            if post.master_id == replyTo:
                new_posts.append(post.as_dict())
            
        posts = new_posts
    
    return posts

@app.route("/user/<username>")
def get_user(username):
    return User.query.filter_by(username=username).first().as_dict()


if __name__ == "__main__":

    app.run(port=3000)




