from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'instance' / 'restaurant.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    with open(BASE_DIR / 'schema.sql', 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    # Seed menu
    menu_count = db.execute('SELECT COUNT(*) as c FROM menu_items').fetchone()[0]
    if menu_count == 0:
        menu_items = [
            ('Margherita Pizza', 'Classic tomato, mozzarella, basil.', 12.99, 'Pizza'),
            ('Truffle Pasta', 'Creamy mushroom pasta with truffle oil.', 16.50, 'Pasta'),
            ('Grilled Salmon', 'Served with lemon herb rice.', 19.90, 'Main'),
            ('Caesar Salad', 'Crisp romaine, parmesan, croutons.', 9.25, 'Salad'),
            ('Tiramisu', 'Coffee-flavored Italian dessert.', 7.50, 'Dessert'),
            ('Fresh Lemonade', 'House-made sparkling lemonade.', 4.75, 'Drinks'),
        ]
        db.executemany(
            'INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)',
            menu_items,
        )
    blog_count = db.execute('SELECT COUNT(*) as c FROM blog_posts').fetchone()[0]
    if blog_count == 0:
        posts = [
            ('Welcome to Savory Haven', 'Discover our story, passion for food, and cozy atmosphere.'),
            ('Chef Special of the Week', 'Every week our chef creates a seasonal signature dish.'),
            ('How We Source Fresh Ingredients', 'We partner with local farms for top-quality produce and meats.'),
        ]
        db.executemany(
            'INSERT INTO blog_posts (title, content) VALUES (?, ?)',
            posts,
        )
    db.commit()
    db.close()


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


@app.route('/')
def home():
    db = get_db()
    featured = db.execute('SELECT * FROM menu_items LIMIT 3').fetchall()
    reviews = db.execute(
        '''SELECT reviews.content, reviews.rating, users.username
           FROM reviews JOIN users ON reviews.user_id = users.id
           ORDER BY reviews.id DESC LIMIT 3'''
    ).fetchall()
    posts = db.execute('SELECT * FROM blog_posts ORDER BY id DESC LIMIT 2').fetchall()
    return render_template('home.html', featured=featured, reviews=reviews, posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))
        db.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, generate_password_hash(password)),
        )
        db.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        user = get_db().execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


@app.route('/menu')
def menu():
    items = get_db().execute('SELECT * FROM menu_items ORDER BY category, id').fetchall()
    return render_template('menu.html', items=items)


@app.route('/blog')
def blog():
    posts = get_db().execute('SELECT * FROM blog_posts ORDER BY id DESC').fetchall()
    return render_template('blog.html', posts=posts)


@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    user = current_user()
    db = get_db()
    if request.method == 'POST':
        if not user:
            flash('Please log in to add a review.', 'warning')
            return redirect(url_for('login'))
        content = request.form['content'].strip()
        rating = int(request.form['rating'])
        if not content:
            flash('Review cannot be empty.', 'danger')
            return redirect(url_for('reviews'))
        db.execute(
            'INSERT INTO reviews (user_id, content, rating) VALUES (?, ?, ?)',
            (user['id'], content, rating),
        )
        db.commit()
        flash('Thank you for your review!', 'success')
        return redirect(url_for('reviews'))
    all_reviews = db.execute(
        '''SELECT reviews.content, reviews.rating, reviews.created_at, users.username
           FROM reviews JOIN users ON reviews.user_id = users.id
           ORDER BY reviews.id DESC'''
    ).fetchall()
    return render_template('reviews.html', reviews=all_reviews)


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        init_db()
    app.run(debug=True)
