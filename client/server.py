from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import platform
import psutil
import time
import subprocess
from functools import wraps

# Load environment
load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'secret-token-kde-bot-2025')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', './screenshots')

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ===========================
# AUTH MIDDLEWARE
# ===========================

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        # Extract token
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header

        if not token:
            logger.warning('❌ Missing auth token')
            return jsonify({'status': 'error', 'message': 'Missing auth token'}), 401

        if token != AUTH_TOKEN:
            logger.warning(f'❌ Invalid token: {token[:10]}... (expected: {AUTH_TOKEN[:10]}...)')
            return jsonify({'status': 'error', 'message': 'Invalid auth token'}), 401

        logger.info('✅ Auth OK')
        return f(*args, **kwargs)

    return decorated


# ===========================
# ROUTES
# ===========================

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'online', 'service': 'KDE Connect Bot Client'}), 200


@app.route('/status', methods=['GET'])
@require_auth
def get_status():
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        uptime_sec = int(time.time() - psutil.boot_time())
        uptime = f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m"

        return jsonify({
            'hostname': platform.node(),
            'os': f"{platform.system()} {platform.release()}",
            'cpu': round(cpu, 1),
            'memory': round(mem.percent, 1),
            'uptime': uptime
        }), 200
    except Exception as e:
        logger.error(f'Status error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/command', methods=['POST'])
@require_auth
def handle_command():
    try:
        data = request.get_json()
        command = data.get('command')
        params = data.get('params', {})

        logger.info(f'📥 Command: {command} | Params: {params}')

        result = execute_command(command, params)
        logger.info(f'📤 Result: {result}')

        return jsonify(result), 200
    except Exception as e:
        logger.error(f'Command error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/upload', methods=['POST'])
@require_auth
def handle_upload():
    try:
        import requests

        data = request.get_json()
        filename = data.get('filename')
        url = data.get('url')

        logger.info(f'📥 Downloading: {filename}')

        filepath = os.path.join(UPLOAD_DIR, filename)
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        logger.info(f'✅ Saved: {filepath}')
        return jsonify({'status': 'success', 'message': 'File saved', 'path': filepath}), 200
    except Exception as e:
        logger.error(f'Upload error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
@require_auth
def download_file(filename):
    try:
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===========================
# COMMAND EXECUTION
# ===========================

def execute_command(command, params):
    os_name = platform.system()

    try:
        if command == 'lock':
            if os_name == 'Linux':
                subprocess.run(['loginctl', 'lock-session'], check=False)
            elif os_name == 'Windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            elif os_name == 'Darwin':
                subprocess.run(
                    ['/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
            return {'status': 'success', 'message': '🔒 Screen locked'}

        elif command == 'volume':
            level = params.get('level', 50)
            if os_name == 'Linux':
                subprocess.run(['amixer', 'set', 'Master', f'{level}%'], check=False)
            elif os_name == 'Windows':
                subprocess.run(['nircmd.exe', 'setsysvolume', str(int(level * 655.35))], check=False)
            elif os_name == 'Darwin':
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'])
            return {'status': 'success', 'message': f'🔊 Volume set to {level}%'}

        elif command == 'mute':
            if os_name == 'Linux':
                subprocess.run(['amixer', 'set', 'Master', 'toggle'], check=False)
            elif os_name == 'Windows':
                subprocess.run(['nircmd.exe', 'mutesysvolume', '2'], check=False)
            elif os_name == 'Darwin':
                subprocess.run(['osascript', '-e', 'set volume with output muted'])
            return {'status': 'success', 'message': '🔇 Mute toggled'}

        elif command == 'copy':
            import pyperclip
            text = params.get('text', '')
            pyperclip.copy(text)
            return {'status': 'success', 'message': '📋 Text copied to clipboard'}

        elif command == 'paste':
            import pyperclip
            content = pyperclip.paste()
            return {'status': 'success', 'message': 'Clipboard content', 'content': content}

        elif command == 'screenshot':
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            filename = f'screenshot_{int(time.time())}.png'
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            screenshot.save(filepath)
            return {'status': 'success', 'message': '📸 Screenshot captured', 'file': filename}

        elif command == 'sleep':
            if os_name == 'Linux':
                subprocess.Popen(['systemctl', 'suspend'])
            elif os_name == 'Windows':
                subprocess.Popen(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
            elif os_name == 'Darwin':
                subprocess.Popen(['pmset', 'sleepnow'])
            return {'status': 'success', 'message': '😴 Going to sleep'}

        elif command == 'shutdown':
            if os_name == 'Linux':
                subprocess.Popen(['shutdown', '-h', 'now'])
            elif os_name == 'Windows':
                subprocess.Popen(['shutdown', '/s', '/t', '5'])
            elif os_name == 'Darwin':
                subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
            return {'status': 'success', 'message': '⚠️ Shutting down...'}

        else:
            return {'status': 'error', 'message': f'Unknown command: {command}'}

    except Exception as e:
        logger.error(f'Execution error: {e}')
        return {'status': 'error', 'message': str(e)}


# ===========================
# START SERVER
# ===========================

if __name__ == '__main__':
    print('\n' + '=' * 60)
    print('🚀 KDE Connect Bot - Python Client')
    print('=' * 60)
    print(f'📡 Host: {HOST}')
    print(f'🔌 Port: {PORT}')
    print(f'🔒 Auth: {"✅ ENABLED" if AUTH_TOKEN else "❌ DISABLED (NOT SECURE!)"}')
    if AUTH_TOKEN:
        print(f'🔑 Token: {AUTH_TOKEN[:10]}...{AUTH_TOKEN[-5:]}')
    print('=' * 60)
    print(f'\n✅ Server running at http://{HOST}:{PORT}')
    print('   Waiting for Telegram bot commands...\n')

    app.run(host=HOST, port=PORT, debug=False, threaded=True)