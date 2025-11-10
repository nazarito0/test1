# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_chat_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# === БАЗА ДАНИХ ===
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_message(username, message):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)",
        (username, message, timestamp)
    )
    conn.commit()
    msg_id = c.lastrowid
    conn.close()
    return msg_id

def get_history(limit=50):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, message, timestamp FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]  # Нові зверху

# === ВЕБ-РОУТИ ===
@app.route('/')
def index():
    history = get_history()
    return render_template('index.html', messages=history)

# === SOCKETIO (реальний час) ===
@socketio.on('connect')
def handle_connect():
    emit('status', {'msg': 'Підключено до чату!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Користувач від\'єднався')

@socketio.on('send_message')
def handle_message(data):
    username = data.get('username', 'Анонім')
    message = data.get('message', '').strip()
    
    if not message:
        return
    
    # Зберігаємо в БД
    msg_id = save_message(username, message)
    
    # Відправляємо всім (broadcast)
    emit('new_message', {
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'id': msg_id
    }, broadcast=True)

#if __name__ == '__main__':
#    init_db()
#    socketio.run(app, host='0.0.0.0', port=5000, debug=True)