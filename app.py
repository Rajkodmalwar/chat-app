# app.py

from flask import Flask, Blueprint, request, session, redirect, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)
db = None

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    return app

def init_auth(database):
    global db
    db = database
    db['users'].create_index("username", unique=True)
    db['users'].create_index("email", unique=True)

def load_html(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db['users'].find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect('/')
        return render_template_string(load_html('login.html'), error="Invalid credentials")
    return render_template_string(load_html('login.html'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)
        if db['users'].find_one({'$or': [{'username': username}, {'email': email}]}):
            return render_template_string(load_html('register.html'), error="User already exists")
        db['users'].insert_one({
            'username': username,
            'email': email,
            'password': hashed,
            'created_at': datetime.utcnow()
        })
        return redirect('/login')
    return render_template_string(load_html('register.html'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
# https://chatgpt.com/share/685a564f-f834-8011-9622-f5ea19affd88