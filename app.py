from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import os
 
app = Flask(__name__)
 
# Change this to your own secret key
app.config["SECRET_KEY"] = "9f4c1c6c8c8c5f5c9d8d0f5f3d3a7e8b2c1d9a0e6f7b8c9d1e2f3a4b5c6d7e8"
 
# IMPORTANT:
# Replace root and YOUR_MYSQL_PASSWORD with your actual MySQL username and password.
# If your Workbench connection uses a different host/port, change them too.
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:3306/restaurant_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
 
db = SQLAlchemy(app)
 
 
class User(db.Model):
    __tablename__ = "users"
 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
 
    reviews = db.relationship("Review", backref="user", lazy=True)
 
 
class Review(db.Model):
    __tablename__ = "reviews"
 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
 
 
class MenuItem(db.Model):
    __tablename__ = "menu_items"
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
 
 
class BlogPost(db.Model):
    __tablename__ = "blog_posts"


 
def seed_data():
    if MenuItem.query.count() == 0:
        menu_items = [
            MenuItem(name="Margherita Pizza", description="Classic tomato, mozzarella, basil.", price=12.99, category="Pizza"),
            MenuItem(name="Truffle Pasta", description="Creamy mushroom pasta with truffle oil.", price=16.50, category="Pasta"),
            MenuItem(name="Grilled Salmon", description="Served with lemon herb rice.", price=19.90, category="Main"),
            MenuItem(name="Caesar Salad", description="Crisp romaine, parmesan, croutons.", price=9.25, category="Salad"),
            MenuItem(name="Tiramisu", description="Coffee-flavored Italian dessert.", price=7.50, category="Dessert"),
            MenuItem(name="Fresh Lemonade", description="House-made sparkling lemonade.", price=4.75, category="Drinks"),
        ]
        db.session.add_all(menu_items)

    if BlogPost.query.count() == 0:
        posts = [
            BlogPost(title="Welcome to Savory Haven", content="Discover our story, passion for food, and cozy atmosphere."),
            BlogPost(title="Chef Special of the Week", content="Every week our chef creates a seasonal signature dish."),
            BlogPost(title="How We Source Fresh Ingredients", content="We partner with local farms for top-quality produce and meats."),
        ]
        db.session.add_all(posts)

    db.session.commit()
 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())



def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@app.context_processor
def inject_user():
    return {"current_user": current_user()}

