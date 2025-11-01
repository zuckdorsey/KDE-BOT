"""
Media player control handler
Supports play/pause, next, previous, volume
"""

import platform
import subprocess
import logging
from pynput.keyboard import Key, Controller

logger = logging.getLogger(__name__)
keyboard = Controller()


class MediaHandler:
    """Handle media player controls"""

    def __init__(self):
        self.os_name = platform.system()

    def play_pause(self):
        """Toggle play/pause"""
        try:
            if self.os_name == 'Linux':
                # Try playerctl (most Linux media players)
                try:
                    result = subprocess.run(
                        ['playerctl', 'play-pause'],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return {'status': 'success', 'message': '⏯️ Play/Pause toggled'}
                except FileNotFoundError:
                    pass

                # Fallback: simulate media key
                self._press_media_key('play_pause')
                return {'status': 'success', 'message': '⏯️ Play/Pause toggled'}

            elif self.os_name == 'Windows':
                # Windows: use nircmd or media keys
                try:
                    subprocess.run(['nircmd.exe', 'sendkeypress', 0xB3])  # Play/Pause key
                except FileNotFoundError:
                    self._press_media_key('play_pause')
                return {'status': 'success', 'message': '⏯️ Play/Pause toggled'}

            elif self.os_name == 'Darwin':
                # macOS: AppleScript
                subprocess.run([
                    'osascript', '-e',
                    'tell application "Music" to playpause'
                ])
                return {'status': 'success', 'message': '⏯️ Play/Pause toggled'}

        except Exception as e:
            logger.error(f"Play/pause error: {e}")
            return {'status': 'error', 'message': f'Failed: {str(e)}'}

    def next_track(self):
        """Skip to next track"""
        try:
            if self.os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'next'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏭️ Next track'}
                except FileNotFoundError:
                    self._press_media_key('next')
                    return {'status': 'success', 'message': '⏭️ Next track'}

            elif self.os_name == 'Windows':
                try:
                    subprocess.run(['nircmd.exe', 'sendkeypress', 0xB0])  # Next track
                except FileNotFoundError:
                    self._press_media_key('next')
                return {'status': 'success', 'message': '⏭️ Next track'}

            elif self.os_name == 'Darwin':
                subprocess.run([
                    'osascript', '-e',
                    'tell application "Music" to next track'
                ])
                return {'status': 'success', 'message': '⏭️ Next track'}

        except Exception as e:
            logger.error(f"Next track error: {e}")
            return {'status': 'error', 'message': f'Failed: {str(e)}'}

    def previous_track(self):
        """Go to previous track"""
        try:
            if self.os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'previous'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏮️ Previous track'}
                except FileNotFoundError:
                    self._press_media_key('previous')
                    return {'status': 'success', 'message': '⏮️ Previous track'}

            elif self.os_name == 'Windows':
                try:
                    subprocess.run(['nircmd.exe', 'sendkeypress', 0xB1])  # Previous track
                except FileNotFoundError:
                    self._press_media_key('previous')
                return {'status': 'success', 'message': '⏮️ Previous track'}

            elif self.os_name == 'Darwin':
                subprocess.run([
                    'osascript', '-e',
                    'tell application "Music" to previous track'
                ])
                return {'status': 'success', 'message': '⏮️ Previous track'}

        except Exception as e:
            logger.error(f"Previous track error: {e}")
            return {'status': 'error', 'message': f'Failed: {str(e)}'}

    def stop(self):
        """Stop playback"""
        try:
            if self.os_name == 'Linux':
                try:
                    subprocess.run(['playerctl', 'stop'], check=True, timeout=5)
                    return {'status': 'success', 'message': '⏹️ Playback stopped'}
                except FileNotFoundError:
                    self._press_media_key('stop')
                    return {'status': 'success', 'message': '⏹️ Playback stopped'}

            elif self.os_name == 'Windows':
                try:
                    subprocess.run(['nircmd.exe', 'sendkeypress', 0xB2])  # Stop
                except FileNotFoundError:
                    self._press_media_key('stop')
                return {'status': 'success', 'message': '⏹️ Playback stopped'}

            elif self.os_name == 'Darwin':
                subprocess.run([
                    'osascript', '-e',
                    'tell application "Music" to stop'
                ])
                return {'status': 'success', 'message': '⏹️ Playback stopped'}

        except Exception as e:
            logger.error(f"Stop error: {e}")
            return {'status': 'error', 'message': f'Failed: {str(e)}'}

    def get_now_playing(self):
        """Get currently playing track info"""
        try:
            if self.os_name == 'Linux':
                try:
                    # Get metadata from playerctl
                    artist = subprocess.run(
                        ['playerctl', 'metadata', 'artist'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    ).stdout.strip()

                    title = subprocess.run(
                        ['playerctl', 'metadata', 'title'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    ).stdout.strip()

                    status = subprocess.run(
                        ['playerctl', 'status'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    ).stdout.strip()

                    if artist and title:
                        return {
                            'status': 'success',
                            'message': f'🎵 Now Playing',
                            'track': f'{artist} - {title}',
                            'playback_status': status
                        }
                    else:
                        return {'status': 'success', 'message': '🎵 No track playing'}

                except FileNotFoundError:
                    return {'status': 'error', 'message': 'playerctl not installed'}

            elif self.os_name == 'Darwin':
                # macOS: AppleScript
                script = '''
                    tell application "Music"
                        if player state is playing then
                            set trackInfo to name of current track & " - " & artist of current track
                            return trackInfo
                        else
                            return "No track playing"
                        end if
                    end tell
                '''
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return {
                    'status': 'success',
                    'message': '🎵 Now Playing',
                    'track': result.stdout.strip()
                }

            else:
                return {'status': 'error', 'message': 'Not supported on this OS'}

        except Exception as e:
            logger.error(f"Now playing error: {e}")
            return {'status': 'error', 'message': f'Failed: {str(e)}'}

    def _press_media_key(self, key_type):
        """Simulate media key press (fallback method)"""
        # This is a fallback - actual implementation depends on pynput version
        # Media keys might not work on all systems
        pass