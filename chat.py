# chat.py

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from raglogic import get_llm_response

chat_bp = Blueprint('chat', __name__)
chat_collection = None

def init_chat(database):
    global chat_collection
    chat_collection = database['chathistory']

@chat_bp.route('/command', methods=['POST'])
def command():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    user_input = data.get('message', '')
    response = get_llm_response(user_input)

    chat_collection.update_one(
        {'user_id': session['username']},
        {'$push': {'chats': {
            'message': user_input,
            'response': response,
            'timestamp': datetime.utcnow()
        }}},
        upsert=True
    )
    return jsonify({'response': response})

@chat_bp.route('/chat_history', methods=['GET'])
def chat_history():
    if 'username' not in session:
        return jsonify([])
    history = chat_collection.find_one({'user_id': session['username']})
    return jsonify(history.get('chats', []) if history else [])
