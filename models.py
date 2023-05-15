from app import db

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

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)
    posts = db.relationship("Post", backref="user", lazy="dynamic")
    
    following = db.relationship('User', secondary=relationships_table,
                                primaryjoin='User.id == follow_relationships.c.follower_id',
                                secondaryjoin='User.id == follow_relationships.c.followed_id',
                                backref='followers')

    def __repr__(self):
        return f'<User "{self.username}">'

class Post(db.Model):
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

class Token(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, primary_key=True)
    exp_date = db.Column(db.DateTime)
    exp = db.Column(db.Boolean, default=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

