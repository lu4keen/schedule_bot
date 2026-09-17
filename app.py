import asyncio
import threading
from flask import Flask
import os
from main import main as start_bot

app = Flask(__name__)
app.route('/')
app.route('/health')

def healthcheck():
    return 'Bot is running', 200

def runbot():
    asyncio.run(start_bot())

if __name__ == '__main__':
    bot_thread = threading.Thread(target=runbot, daemon=True)
    bot_thread.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
