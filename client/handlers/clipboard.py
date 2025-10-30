import pyperclip


class ClipboardHandler:
    """Handle clipboard operations"""

    def copy(self, text):
        """Copy text to clipboard"""
        try:
            pyperclip.copy(text)
            return {
                'status': 'success',
                'message': '📋 Text copied to clipboard'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to copy: {str(e)}'
            }

    def paste(self):
        """Get clipboard content"""
        try:
            content = pyperclip.paste()
            return {
                'status': 'success',
                'message': 'Clipboard content retrieved',
                'content': content
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to paste: {str(e)}'
            }