
from flask import request
from app import db
from models import Post, User

from flask import current_app as app


@app.route("/posts", methods=["GET"])
def posts():
    by = request.args.get("by")
    likedBy = request.args.get("likedBy")
    id = request.args.get("id")
    madeAfter = request.args.get("madeAfter")
    replyTo = request.args.get("replyTo")

    if id:
        return [Post.query.get(id)]
    
    posts = Post.query.all()

    if by:
        new_posts = []
        for post in posts:
            if post.user == by:
                new_posts.append(post)
        
        posts = new_posts
    
    if likedBy:
        new_posts = []
        for post in posts:
            if post.likes.contains(likedBy):
                new_posts.append(post)
        
        posts = new_posts
    
    if replyTo:
        new_posts = []
        for post in posts:
            if post.master_id == replyTo:
                new_posts.append(post)
            
        posts = new_posts
    
    return posts

@app.route("/user/<username>")
def get_user(username):
    return User.query.filter_by(username=username).first()


