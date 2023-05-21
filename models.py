from app import db
from sqlalchemy_serializer import SerializerMixin
from dataclasses import dataclass

relationships_table = db.Table('follow_relationships',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))                
)

likes_table = db.Table('likes',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('liker_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

def list_to_string(list):
    str_list = []
    for item in list:
        str_list.append(str(item))

    return str_list

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)
    posts = db.relationship("Post", backref="user")
    
    following = db.relationship('User', secondary=relationships_table,
                                primaryjoin='User.id == follow_relationships.c.follower_id',
                                secondaryjoin='User.id == follow_relationships.c.followed_id',
                                backref='followers')

    def __repr__(self):
        return self.username

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "bio": self.bio,
            "posts": list_to_string(self.posts),
            "following": list_to_string(self.following),
            "followers": list_to_string(self.followers),
            "liked_posts": list_to_string(self.liked_posts)
        }


class Token(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String)
    exp_date = db.Column(db.DateTime)
    exp = db.Column(db.Boolean, default=False)

class Post(db.Model, SerializerMixin):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    master_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime)

    likes = db.relationship('User', secondary=likes_table,
                            primaryjoin='Post.id == likes.c.post_id',
                            secondaryjoin='User.id == likes.c.liker_id',
                            backref="liked_posts")

    def __repr__(self):
        return str(self.id)

    def as_dict(self):

        return {
            "id": self.id,
            "content": self.content,
            "master_id": self.master_id,
            "user_id": self.user_id,
            "date_created": str(self.date_created),
            "likes": list_to_string(self.likes),
            "user": str(self.user)
        }


