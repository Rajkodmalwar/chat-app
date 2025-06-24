# ragSEARCH.py

from pymongo import MongoClient
from app import auth_bp, init_auth, create_app, load_html
from chat import chat_bp, init_chat
from flask import session, redirect, render_template_string

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['chatdb']

# Create Flask app
app = create_app()

# Initialize Blueprints
init_auth(db)
init_chat(db)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

@app.route('/')
def home():
    if 'username' in session:
        return render_template_string(load_html('index.html'), username=session['username'])
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
