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
# COMMAND EXECUTION (EXTENDED FOR V1.1)
# ===========================

def execute_command(command, params):
    os_name = platform.system()

    try:
        # ===== EXISTING COMMANDS =====
        if command == 'lock':
            if os_name == 'Linux':
                subprocess.run(['loginctl', 'lock-session'], check=False)
            elif os_name == 'Windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            elif os_name == 'Darwin':
                subprocess.run(
                    ['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
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
            # Using scrot as per your implementation
            if os_name != 'Linux':
                return {'status': 'error', 'message': 'Screenshot only supported on Linux'}

            env = os.environ.copy()
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'

            filename = f'screenshot_{int(time.time())}.png'
            filepath = os.path.join(SCREENSHOT_DIR, filename)

            result = subprocess.run(['scrot', '-z', filepath], env=env, capture_output=True, timeout=10)

            if result.returncode == 0 and os.path.exists(filepath):
                return {'status': 'success', 'message': '📸 Screenshot captured', 'file': filename}
            else:
                return {'status': 'error', 'message': 'Screenshot failed. Install scrot: sudo pacman -S scrot'}

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

        # ===== NEW V1.1 COMMANDS =====

        # Media Player Control
        elif command == 'media_play_pause':
            if os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'play-pause'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏯️ Play/Pause toggled'}
                except FileNotFoundError:
                    return {'status': 'error', 'message': 'playerctl not installed. Install: sudo pacman -S playerctl'}
            return {'status': 'error', 'message': 'Not supported on this OS'}

        elif command == 'media_next':
            if os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'next'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏭️ Next track'}
                except FileNotFoundError:
                    return {'status': 'error', 'message': 'playerctl not installed'}
            return {'status': 'error', 'message': 'Not supported on this OS'}

        elif command == 'media_previous':
            if os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'previous'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏮️ Previous track'}
                except FileNotFoundError:
                    return {'status': 'error', 'message': 'playerctl not installed'}
            return {'status': 'error', 'message': 'Not supported on this OS'}

        elif command == 'media_stop':
            if os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'stop'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏹️ Playback stopped'}
                except FileNotFoundError:
                    return {'status': 'error', 'message': 'playerctl not installed'}
            return {'status': 'error', 'message': 'Not supported on this OS'}

        elif command == 'media_now_playing':
            if os_name == 'Linux':
                try:
                    artist = subprocess.run(['playerctl', 'metadata', 'artist'], capture_output=True, text=True,
                                            timeout=5).stdout.strip()
                    title = subprocess.run(['playerctl', 'metadata', 'title'], capture_output=True, text=True,
                                           timeout=5).stdout.strip()
                    status = subprocess.run(['playerctl', 'status'], capture_output=True, text=True,
                                            timeout=5).stdout.strip()

                    if artist and title:
                        return {
                            'status': 'success',
                            'message': '🎵 Now Playing',
                            'track': f'{artist} - {title}',
                            'playback_status': status
                        }
                    return {'status': 'success', 'message': '🎵 No track playing'}
                except FileNotFoundError:
                    return {'status': 'error', 'message': 'playerctl not installed'}
            return {'status': 'error', 'message': 'Not supported on this OS'}

        # Battery Status
        elif command == 'battery_status':
            battery = psutil.sensors_battery()

            if battery is None:
                return {'status': 'success', 'message': '🔌 No battery detected (Desktop PC)', 'has_battery': False}

            percent = battery.percent
            plugged = battery.power_plugged
            charging_status = '🔌 Charging' if plugged else '🔋 On Battery'

            time_remaining = battery.secsleft
            if time_remaining == psutil.POWER_TIME_UNLIMITED:
                time_str = 'Unlimited (Plugged in)'
            elif time_remaining == psutil.POWER_TIME_UNKNOWN:
                time_str = 'Unknown'
            else:
                hours = time_remaining // 3600
                minutes = (time_remaining % 3600) // 60
                time_str = f'{hours}h {minutes}m remaining'

            icon = '🔋' if percent >= 30 else '⚠️' if percent >= 15 else '❗'

            details = f'{icon} {percent}% - {charging_status}\n⏱️ {time_str}'

            return {
                'status': 'success',
                'message': f'{icon} Battery Status',
                'percent': percent,
                'charging': plugged,
                'details': details
            }

        # Network Information
        elif command == 'network_info':
            import socket

            hostname = socket.gethostname()

            # Get interfaces
            interfaces = []
            stats = psutil.net_if_addrs()
            for iface, addrs in stats.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                        interfaces.append({'name': iface, 'ip': addr.address})

            details = f"🖥️ Hostname: {hostname}\n\n"
            if interfaces:
                details += "📡 Network Interfaces:\n"
                for iface in interfaces:
                    details += f"  • {iface['name']}: {iface['ip']}\n"

            return {
                'status': 'success',
                'message': '🌐 Network Information',
                'hostname': hostname,
                'interfaces': interfaces,
                'details': details
            }

        elif command == 'network_stats':
            stats = psutil.net_io_counters()

            def bytes_to_human(n):
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if n < 1024.0:
                        return f"{n:.2f} {unit}"
                    n /= 1024.0

            details = (
                f"📤 Sent: {bytes_to_human(stats.bytes_sent)}\n"
                f"📥 Received: {bytes_to_human(stats.bytes_recv)}\n"
                f"📦 Packets Sent: {stats.packets_sent:,}\n"
                f"📦 Packets Recv: {stats.packets_recv:,}"
            )

            return {
                'status': 'success',
                'message': '📊 Network Statistics',
                'sent': bytes_to_human(stats.bytes_sent),
                'received': bytes_to_human(stats.bytes_recv),
                'details': details
            }

        # Process Management
        elif command == 'process_list':
            sort_by = params.get('sort_by', 'cpu')
            limit = params.get('limit', 10)

            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu': info['cpu_percent'] or 0,
                        'memory': info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu'], reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory'], reverse=True)

            top_processes = processes[:limit]

            details = f"🔝 Top {limit} Processes (by {sort_by.upper()}):\n\n"
            for i, proc in enumerate(top_processes, 1):
                details += f"{i}. {proc['name']}\n   PID: {proc['pid']} | CPU: {proc['cpu']:.1f}% | RAM: {proc['memory']:.1f}%\n\n"

            return {
                'status': 'success',
                'message': '💻 Process List',
                'processes': top_processes,
                'details': details
            }

        elif command == 'process_search':
            name = params.get('name', '')
            matches = []

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        matches.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu': proc.info['cpu_percent'] or 0,
                            'memory': proc.info['memory_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if not matches:
                return {'status': 'success', 'message': f'🔍 No processes found matching: {name}'}

            details = f"🔍 Found {len(matches)} process(es) matching '{name}':\n\n"
            for proc in matches:
                details += f"• {proc['name']}\n  PID: {proc['pid']} | CPU: {proc['cpu']:.1f}% | RAM: {proc['memory']:.1f}%\n\n"

            return {
                'status': 'success',
                'message': f'🔍 Search Results',
                'processes': matches,
                'details': details
            }

        elif command == 'process_kill':
            pid = params.get('pid')
            try:
                process = psutil.Process(pid)
                name = process.name()
                process.terminate()
                process.wait(timeout=5)
                return {'status': 'success', 'message': f'✅ Process killed: {name} (PID: {pid})'}
            except psutil.NoSuchProcess:
                return {'status': 'error', 'message': f'❌ Process not found (PID: {pid})'}
            except psutil.AccessDenied:
                return {'status': 'error', 'message': f'❌ Access denied (PID: {pid})'}

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
    print('🚀 KDE Connect Bot - Python Client v1.1')
    print('=' * 60)
    print(f'📡 Host: {HOST}')
    print(f'🔌 Port: {PORT}')
    print(f'🔒 Auth: {"✅ ENABLED" if AUTH_TOKEN else "❌ DISABLED"}')
    if AUTH_TOKEN:
        print(f'🔑 Token: {AUTH_TOKEN[:10]}...{AUTH_TOKEN[-5:]}')
    print('\n🆕 Version 1.1 Features:')
    print('   ✅ Media player control (playerctl)')
    print('   ✅ Battery status monitoring')
    print('   ✅ Network information')
    print('   ✅ Process management')
    print('=' * 60)
    print(f'\n✅ Server running at http://{HOST}:{PORT}')
    print('   Waiting for Telegram bot commands...\n')

    app.run(host=HOST, port=PORT, debug=False, threaded=True)