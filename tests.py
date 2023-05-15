from app import app, db
from models import User, Post, Token

def load_user_posts(username):
    user = User.query.filter_by(username=username).first()

    for post in user.posts:
        print(post.content)

if __name__ == "__main__":
    with app.app_context():
        load_user_posts("jim")
