from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import platform
import psutil
import time
import subprocess
from functools import wraps
from io import BytesIO
import socket
import mimetypes

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
# (Optional) batasi download ke direktori ini saja (boleh ditambah)
ALLOWED_DOWNLOAD_DIRS = [
    os.path.abspath(UPLOAD_DIR),
    os.path.abspath(SCREENSHOT_DIR),
]

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

        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header

        if not token:
            logger.warning('❌ Missing auth token')
            return jsonify({'status': 'error', 'message': 'Missing auth token'}), 401

        if token != AUTH_TOKEN:
            logger.warning('❌ Invalid token attempt')
            return jsonify({'status': 'error', 'message': 'Invalid auth token'}), 401

        return f(*args, **kwargs)

    return decorated


# ===========================
# BASIC ROUTES
# ===========================

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'online', 'service': 'KDE Connect Bot Client v1.1'}), 200


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


# ===========================
# COMMAND ROUTE
# ===========================

@app.route('/command', methods=['POST'])
@require_auth
def handle_command():
    try:
        data = request.get_json(force=True)
        command = data.get('command')
        params = data.get('params', {}) or {}

        logger.info(f'📥 Command: {command} | Params: {params}')

        result = execute_command(command, params)
        logger.info(f'📤 Result: {result}')

        return jsonify(result), 200
    except Exception as e:
        logger.error(f'Command error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===========================
# FILE UPLOAD
# ===========================

@app.route('/upload', methods=['POST'])
@require_auth
def handle_upload():
    try:
        import requests
        data = request.get_json(force=True)
        filename = (data.get('filename') or '').strip()
        url = data.get('url')

        if not filename or not url:
            return jsonify({'status': 'error', 'message': 'Missing filename or url'}), 400

        # Sanitasi nama file sederhana
        filename = os.path.basename(filename)
        filepath = os.path.join(UPLOAD_DIR, filename)

        logger.info(f'📥 Downloading from Telegram: {filename}')

        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        logger.info(f'✅ Saved: {filepath}')
        return jsonify({'status': 'success', 'message': 'File saved', 'path': filepath}), 200
    except Exception as e:
        logger.error(f'Upload error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===========================
# FILE DOWNLOAD (generic)
# ===========================

@app.route('/getfile', methods=['POST'])
@require_auth
def get_file_generic():
    """
    Download arbitrary file by path (used by bot for user-supplied paths).
    Restrict to ALLOWED_DOWNLOAD_DIRS to avoid traversal abuse.
    """
    try:
        data = request.get_json(force=True)
        path_req = data.get('path', '').strip()

        if not path_req:
            return jsonify({'status': 'error', 'message': 'Path required'}), 400

        abs_path = os.path.abspath(path_req)

        # Allow if inside one of allowed dirs OR exact file exists and user intentionally wants it (optional).
        if not any(abs_path.startswith(allowed + os.sep) or abs_path == allowed for allowed in ALLOWED_DOWNLOAD_DIRS):
            return jsonify({'status': 'error', 'message': 'Access denied to this path'}), 403

        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        # Stream the file
        mime, _ = mimetypes.guess_type(abs_path)
        mime = mime or 'application/octet-stream'
        return send_file(abs_path, mimetype=mime, as_attachment=True,
                         download_name=os.path.basename(abs_path))
    except Exception as e:
        logger.error(f'Download error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Existing screenshot download route (unchanged)
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
        # -------- CORE (sudah ada) --------
        if command == 'lock':
            if os_name == 'Linux':
                subprocess.run(['loginctl', 'lock-session'], check=False)
            elif os_name == 'Windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            elif os_name == 'Darwin':
                subprocess.run(['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
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
            if os_name != 'Linux':
                return {'status': 'error', 'message': 'Screenshot only implemented for Linux in this build'}
            env = os.environ.copy()
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'
            filename = f'screenshot_{int(time.time())}.png'
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            result = subprocess.run(['scrot', '-z', filepath], env=env, capture_output=True)
            if result.returncode == 0 and os.path.exists(filepath):
                return {'status': 'success', 'message': '📸 Screenshot captured', 'file': filename}
            return {'status': 'error', 'message': 'Failed to capture screenshot (scrot). Install/pastikan DISPLAY benar.'}

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
                subprocess.Popen(['shutdown', '-h', '+1'])
            elif os_name == 'Windows':
                subprocess.Popen(['shutdown', '/s', '/t', '60'])
            elif os_name == 'Darwin':
                subprocess.Popen(['sudo', 'shutdown', '-h', '+1'])
            return {'status': 'success', 'message': '⚠️ Shutting down in 1 minute...'}

        # -------- NEW (battery / network) --------
        elif command == 'battery_status':
            try:
                battery = psutil.sensors_battery()
            except Exception:
                battery = None
            if battery is None:
                return {
                    'status': 'success',
                    'message': '🔌 No battery detected',
                    'details': '🔌 Deskop / Tidak ada battery terdeteksi'
                }
            percent = battery.percent
            plugged = battery.power_plugged
            time_left = battery.secsleft
            if time_left in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
                tl = 'Unknown'
            else:
                h = time_left // 3600
                m = (time_left % 3600) // 60
                tl = f'{h}h {m}m remaining'
            icon = '🔋' if percent >= 30 else '⚠️'
            details = f"{icon} {percent}% - {'Charging' if plugged else 'On Battery'}\n⏱️ {tl}"
            return {
                'status': 'success',
                'message': f'{icon} Battery {percent}%',
                'percent': percent,
                'charging': plugged,
                'details': details
            }

        elif command == 'network_info':
            hostname = socket.gethostname()
            # Gather interface IPv4
            interfaces = []
            try:
                for name, addrs in psutil.net_if_addrs().items():
                    for a in addrs:
                        if a.family == socket.AF_INET and a.address != '127.0.0.1':
                            interfaces.append({'iface': name, 'ip': a.address})
            except Exception:
                pass
            details = f"🖥️ Host: {hostname}\n"
            if interfaces:
                details += "📡 Interfaces:\n" + "\n".join([f" - {i['iface']}: {i['ip']}" for i in interfaces])
            else:
                details += "📡 No active non-loopback IPv4 interface"
            return {
                'status': 'success',
                'message': '🌐 Network Info',
                'interfaces': interfaces,
                'details': details
            }

        elif command == 'network_stats':
            try:
                io = psutil.net_io_counters()
                def human(b):
                    for unit in ['B','KB','MB','GB','TB']:
                        if b < 1024:
                            return f"{b:.2f} {unit}"
                        b /= 1024
                details = (
                    f"📊 Network Stats\n"
                    f"📤 Sent: {human(io.bytes_sent)}\n"
                    f"📥 Received: {human(io.bytes_recv)}\n"
                    f"📦 Packets Sent: {io.packets_sent}\n"
                    f"📦 Packets Recv: {io.packets_recv}"
                )
                return {
                    'status': 'success',
                    'message': '📊 Network Statistics',
                    'details': details
                }
            except Exception as e:
                return {'status': 'error', 'message': f'Failed to read network stats: {e}'}

        # -------- Unknown --------
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
    print('🚀 KDE Connect Bot - Python Client (Enhanced)')
    print('=' * 60)
    print(f'📡 Host: {HOST}:{PORT}')
    print(f'🔒 Auth: {"✅ ENABLED" if AUTH_TOKEN else "❌ DISABLED"}')
    print(f'📁 Upload dir: {os.path.abspath(UPLOAD_DIR)}')
    print(f'🖼️ Screenshot dir: {os.path.abspath(SCREENSHOT_DIR)}')
    print('=' * 60)
    app.run(host=HOST, port=PORT, debug=False, threaded=True)