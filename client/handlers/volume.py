import platform
import subprocess


class VolumeHandler:
    """Handle volume control"""

    def __init__(self):
        self.os_name = platform.system()

    def set_volume(self, level):
        """Set system volume (0-100)"""
        try:
            if self.os_name == 'Windows':
                # Using nircmd (needs to be installed)
                subprocess.run(['nircmd.exe', 'setsysvolume', str(int(level * 655.35))])
            elif self.os_name == 'Linux':
                subprocess.run(['amixer', 'set', 'Master', f'{level}%'])
            elif self.os_name == 'Darwin':
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'])

            return {
                'status': 'success',
                'message': f'🔊 Volume set to {level}%'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to set volume: {str(e)}'
            }

    def toggle_mute(self):
        """Toggle mute/unmute"""
        try:
            if self.os_name == 'Windows':
                subprocess.run(['nircmd.exe', 'mutesysvolume', '2'])
            elif self.os_name == 'Linux':
                subprocess.run(['amixer', 'set', 'Master', 'toggle'])
            elif self.os_name == 'Darwin':
                subprocess.run(['osascript', '-e', 'set volume with output muted'])

            return {
                'status': 'success',
                'message': '🔇 Mute toggled'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to toggle mute: {str(e)}'
            }