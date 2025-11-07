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
import socket
import mimetypes
from typing import Callable, Dict, Any

# Modular handlers
from handlers.system import SystemHandler
from handlers.clipboard import ClipboardHandler
from handlers.volume import VolumeHandler
from handlers.network import NetworkHandler
from handlers.battery import BatteryHandler
from handlers.process import ProcessHandler
from handlers.media import MediaHandler

# Load environment
load_dotenv()

app = Flask(__name__)
CORS(app)

AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'secret-token-kde-bot-2025')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', './screenshots')
ALLOWED_DOWNLOAD_DIRS = [os.path.abspath(UPLOAD_DIR), os.path.abspath(SCREENSHOT_DIR)]

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


###############################################################################
# Command dispatch (refactored to modular handlers)
###############################################################################

# Instantiate handlers once (reduces per-call overhead)
system_handler = SystemHandler({'SCREENSHOT_DIR': SCREENSHOT_DIR})
clipboard_handler = ClipboardHandler()
volume_handler = VolumeHandler()
network_handler = NetworkHandler()
battery_handler = BatteryHandler()
process_handler = ProcessHandler()
media_handler = MediaHandler()

def _wrap(func: Callable[[Dict[str, Any]], Dict[str, Any]], expects_params: bool = False) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    def inner(params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if expects_params:
                return func(params)
            return func({})  # if signature expects but unused
        except Exception as e:
            logger.error(f'Handler error: {e}')
            return {'status': 'error', 'message': str(e)}
    return inner

# Map command -> callable receiving params dict and returning result dict
def _cmd_lock(_):
    return system_handler.lock_screen()
def _cmd_sleep(_):
    return system_handler.sleep()
def _cmd_shutdown(_):
    return system_handler.shutdown()
def _cmd_screenshot(_):
    return system_handler.take_screenshot()
def _cmd_copy(p):
    return clipboard_handler.copy(p.get('text', ''))
def _cmd_paste(_):
    return clipboard_handler.paste()
def _cmd_volume(p):
    return volume_handler.set_volume(p.get('level', 50))
def _cmd_mute(_):
    return volume_handler.toggle_mute()
def _cmd_battery(_):
    return battery_handler.get_battery_status()
def _cmd_network_info(_):
    return network_handler.get_network_info()
def _cmd_network_stats(_):
    return network_handler.get_network_stats()
def _cmd_process_list(p):
    return process_handler.list_processes(limit=p.get('limit', 10), sort_by=p.get('sort_by', 'cpu'))
def _cmd_process_kill(p):
    pid = p.get('pid')
    if pid is None:
        return {'status': 'error', 'message': 'pid required'}
    return process_handler.kill_process(pid)
def _cmd_media_play_pause(_):
    return media_handler.play_pause()
def _cmd_media_next(_):
    return media_handler.next_track()
def _cmd_media_previous(_):
    return media_handler.previous_track()
def _cmd_media_stop(_):
    return media_handler.stop()
def _cmd_media_now_playing(_):
    return media_handler.get_now_playing()

COMMAND_MAP: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    'lock': _cmd_lock,
    'sleep': _cmd_sleep,
    'shutdown': _cmd_shutdown,
    'screenshot': _cmd_screenshot,
    'copy': _cmd_copy,
    'paste': _cmd_paste,
    'volume': _cmd_volume,
    'mute': _cmd_mute,
    'battery_status': _cmd_battery,
    'network_info': _cmd_network_info,
    'network_stats': _cmd_network_stats,
    'process_list': _cmd_process_list,
    'process_kill': _cmd_process_kill,
    'media_play_pause': _cmd_media_play_pause,
    'media_next': _cmd_media_next,
    'media_previous': _cmd_media_previous,
    'media_stop': _cmd_media_stop,
    'media_now_playing': _cmd_media_now_playing,
}

@app.route('/command', methods=['POST'])
@require_auth
def handle_command():
    try:
        data = request.get_json(force=True)
        command = data.get('command') or ''
        params = data.get('params', {}) or {}
        logger.info(f'📥 Command: {command} | Params: {params}')
        handler = COMMAND_MAP.get(command)
        if not handler:
            return jsonify({'status': 'error', 'message': f'Unknown command: {command}'}), 400
        result = handler(params)
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

# Legacy execute_command kept for backward compatibility (delegates to map)
def execute_command(command: str, params: Dict[str, Any]):
    handler = COMMAND_MAP.get(command)
    if not handler:
        return {'status': 'error', 'message': f'Unknown command: {command}'}
    try:
        return handler(params or {})
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