from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = ".&b..M1bU8/<r21#@fo90c"

db.init_app(app)

def wipe_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

