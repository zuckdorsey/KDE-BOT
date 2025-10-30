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
        """
        Take screenshot using SCROT only
        Most reliable method for Arch Linux
        """

        if self.os_name != 'Linux':
            return {
                'status': 'error',
                'message': 'Screenshot only supported on Linux with scrot'
            }

        timestamp = int(time.time())
        filename = f'screenshot_{timestamp}.png'
        filepath = os.path.join(self.config['SCREENSHOT_DIR'], filename)

        logger.info(f"Taking screenshot with scrot: {filename}")

        try:
            # Ensure DISPLAY is set
            env = os.environ.copy()
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'
                logger.info("DISPLAY not set, using :0")

            logger.info(f"Environment DISPLAY: {env.get('DISPLAY')}")

            # Run scrot
            result = subprocess.run(
                ['scrot', '-z', filepath],  # -z = compression
                env=env,
                capture_output=True,
                timeout=10,
                check=False
            )

            # Check if scrot succeeded
            if result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                size = os.path.getsize(filepath)
                logger.info(f"✅ Screenshot success: {size} bytes")
                return {
                    'status': 'success',
                    'message': '📸 Screenshot captured with scrot',
                    'file': filename,
                    'size': size
                }
            else:
                # scrot failed
                stderr = result.stderr.decode() if result.stderr else 'No error output'
                logger.error(f"❌ scrot failed: {stderr}")

                return {
                    'status': 'error',
                    'message': f'scrot failed: {stderr}\n\nMake sure scrot is installed:\nsudo pacman -S scrot'
                }

        except FileNotFoundError:
            logger.error("❌ scrot not found")
            return {
                'status': 'error',
                'message': 'scrot not installed.\n\nInstall it:\nsudo pacman -S scrot'
            }

        except subprocess.TimeoutExpired:
            logger.error("❌ scrot timeout")
            return {
                'status': 'error',
                'message': 'Screenshot timeout. Try again.'
            }

        except Exception as e:
            logger.error(f"❌ Screenshot error: {e}")
            return {
                'status': 'error',
                'message': f'Screenshot failed: {str(e)}'
            }