"""
System handler - Using SCROT ONLY for screenshots
Simple and reliable for Arch Linux
"""

import platform
import psutil
import subprocess
import os
import time
import logging

logger = logging.getLogger(__name__)


class SystemHandler:
    """Handle system-level operations"""

    def __init__(self, config):
        self.config = config
        self.os_name = platform.system()

        logger.info(f"System initialized: {self.os_name}")

    def get_status(self):
        """Get system status information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        uptime_seconds = int(time.time() - psutil.boot_time())

        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime = f"{hours}h {minutes}m"

        return {
            'hostname': platform.node(),
            'os': f"{platform.system()} {platform.release()}",
            'cpu': round(cpu_percent, 1),
            'memory': round(memory.percent, 1),
            'uptime': uptime
        }

    # ===========================
    # FUNCTION execute_lock_screen()
    # ===========================

    def lock_screen(self):
        """
        TRY:
            OS.execute("lock screen command")
            RETURN { "status": "success", "message": "Screen locked" }
        CATCH:
            RETURN { "status": "error", "message": "Failed to lock screen" }
        """
        try:
            if self.os_name == 'Linux':
                # Try loginctl first (most reliable)
                result = subprocess.run(
                    ['loginctl', 'lock-session'],
                    capture_output=True,
                    timeout=5
                )

                if result.returncode == 0:
                    return {'status': 'success', 'message': '🔒 Screen locked'}

                # Fallback to xdg-screensaver
                subprocess.run(['xdg-screensaver', 'lock'], check=True, timeout=5)
                return {'status': 'success', 'message': '🔒 Screen locked'}

            elif self.os_name == 'Windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
                return {'status': 'success', 'message': '🔒 Screen locked'}

            elif self.os_name == 'Darwin':
                subprocess.run(['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
                return {'status': 'success', 'message': '🔒 Screen locked'}

        except Exception as e:
            logger.error(f"Lock screen failed: {e}")
            return {'status': 'error', 'message': f'Failed to lock screen: {str(e)}'}

    def sleep(self):
        """Put computer to sleep"""
        try:
            if self.os_name == 'Linux':
                subprocess.Popen(['systemctl', 'suspend'])
            elif self.os_name == 'Windows':
                subprocess.Popen(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
            elif self.os_name == 'Darwin':
                subprocess.Popen(['pmset', 'sleepnow'])

            return {'status': 'success', 'message': '😴 Going to sleep...'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def shutdown(self):
        """Shutdown computer"""
        try:
            if self.os_name == 'Linux':
                subprocess.Popen(['shutdown', '-h', '+1'])
            elif self.os_name == 'Windows':
                subprocess.Popen(['shutdown', '/s', '/t', '60'])
            elif self.os_name == 'Darwin':
                subprocess.Popen(['sudo', 'shutdown', '-h', '+1'])

            return {'status': 'success', 'message': '⚠️ Shutting down in 1 minute...'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ===========================
    # SCREENSHOT - SCROT ONLY
    # ===========================

    def take_screenshot(self):
        """Take a screenshot with best-effort tool selection.

        - Wayland: prefer grim (sway/Hyprland), then spectacle (KDE), then gnome-screenshot.
        - X11: use scrot with DISPLAY fallback.
        Notes:
        - Black screenshots typically mean capturing under Wayland with X11 tools (scrot) or locked session.
        - This method tries multiple tools and returns first successful capture.
        """

        if self.os_name != 'Linux':
            return {'status': 'error', 'message': 'Screenshot supported on Linux only in this build'}

        timestamp = int(time.time())
        filename = f'screenshot_{timestamp}.png'
        filepath = os.path.join(self.config['SCREENSHOT_DIR'], filename)

        env = os.environ.copy()
        session_type = env.get('XDG_SESSION_TYPE', '').lower()
        desktop_env = (env.get('XDG_CURRENT_DESKTOP') or env.get('DESKTOP_SESSION') or '').lower()
        logger.info(f"Screenshot session: {session_type or 'unknown'} | desktop: {desktop_env or 'unknown'}")

        def _exists(cmd):
            return subprocess.call(['which', cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

        def _ok(path):
            # Some black screenshots are tiny (just header). Require minimal size.
            return os.path.exists(path) and os.path.getsize(path) > 2000

        try:
            cmds_tried = []

            # Wayland-first strategies
            if session_type == 'wayland':
                # GNOME Wayland: grim usually produces black. Prefer gnome-screenshot if available.
                is_gnome = 'gnome' in desktop_env

                if not is_gnome and _exists('grim'):
                    cmds_tried.append('grim')
                    res = subprocess.run(['grim', filepath], capture_output=True, timeout=10)
                    if res.returncode == 0 and _ok(filepath):
                        size = os.path.getsize(filepath)
                        return {'status': 'success', 'message': '📸 Screenshot captured (grim)', 'file': filename, 'size': size}
                    else:
                        logger.warning('grim captured but file invalid or black')

                # GNOME or fallback: try gnome-screenshot first
                if _exists('gnome-screenshot'):
                    cmds_tried.append('gnome-screenshot')
                    res = subprocess.run(['gnome-screenshot', '-f', filepath], capture_output=True, timeout=15)
                    if res.returncode == 0 and _ok(filepath):
                        size = os.path.getsize(filepath)
                        return {'status': 'success', 'message': '📸 Screenshot captured (gnome-screenshot)', 'file': filename, 'size': size}
                    else:
                        logger.warning('gnome-screenshot returned but file invalid or black')

                # KDE Wayland alternative
                if _exists('spectacle'):
                    cmds_tried.append('spectacle')
                    res = subprocess.run(['spectacle', '--noninteractive', '--background', '--output', filepath], capture_output=True, timeout=15)
                    if res.returncode == 0 and _ok(filepath):
                        size = os.path.getsize(filepath)
                        return {'status': 'success', 'message': '📸 Screenshot captured (spectacle)', 'file': filename, 'size': size}
                    else:
                        logger.warning('spectacle returned but file invalid or black')

                # Fallback X11 tools (often black under Wayland, but attempt)
                if 'DISPLAY' not in env:
                    env['DISPLAY'] = ':0'
                if _exists('scrot'):
                    cmds_tried.append('scrot')
                    res = subprocess.run(['scrot', '-z', filepath], env=env, capture_output=True, timeout=10)
                    if res.returncode == 0 and _ok(filepath):
                        size = os.path.getsize(filepath)
                        return {'status': 'success', 'message': '📸 Screenshot captured (scrot via XWayland)', 'file': filename, 'size': size}
                if _exists('maim'):
                    cmds_tried.append('maim')
                    res = subprocess.run(['maim', filepath], env=env, capture_output=True, timeout=10)
                    if res.returncode == 0 and _ok(filepath):
                        size = os.path.getsize(filepath)
                        return {'status': 'success', 'message': '📸 Screenshot captured (maim via XWayland)', 'file': filename, 'size': size}

                # Portal suggestion if all fail
                portal_hint = 'Install gnome-screenshot (GNOME) or use xdg-desktop-portal screenshot tools.'
                return {
                    'status': 'error',
                    'message': 'Failed to capture on Wayland. ' + portal_hint + '\nTried: ' + (', '.join(cmds_tried) or 'none')
                }

            # X11 path (default)
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'
            if _exists('scrot'):
                cmds_tried.append('scrot')
                res = subprocess.run(['scrot', '-z', filepath], env=env, capture_output=True, timeout=10)
                if res.returncode == 0 and _ok(filepath):
                    size = os.path.getsize(filepath)
                    return {'status': 'success', 'message': '📸 Screenshot captured (scrot)', 'file': filename, 'size': size}

            # Secondary X11 tools
            if _exists('maim'):
                cmds_tried.append('maim')
                res = subprocess.run(['maim', filepath], env=env, capture_output=True, timeout=10)
                if res.returncode == 0 and _ok(filepath):
                    size = os.path.getsize(filepath)
                    return {'status': 'success', 'message': '📸 Screenshot captured (maim)', 'file': filename, 'size': size}

            return {
                'status': 'error',
                'message': 'No working screenshot tool found. Install scrot (X11) or grim/spectacle/gnome-screenshot (Wayland).\nTried: ' + ', '.join(cmds_tried) or 'none'
            }

        except subprocess.TimeoutExpired:
            return {'status': 'error', 'message': 'Screenshot timeout. Try again.'}
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return {'status': 'error', 'message': f'Screenshot failed: {str(e)}'}