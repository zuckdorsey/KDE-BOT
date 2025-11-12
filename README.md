# 🤖 Telegram KDE Connect Bot

A local system control solution using Telegram as the interface, mimicking KDE Connect functionality. Control your PC remotely through Telegram messages with a dual-component architecture.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Development](#development)
- [License](#license)

---

## 🌟 Overview

This project implements a **local KDE Connect-like system** where:
- A **Telegram bot** serves as the remote control interface
- A **Python Flask server** executes system commands on your PC
- Both components run on the **same machine (localhost)**
- Communication happens via **HTTP** with token authentication
- **No cloud hosting** required - completely offline except for Telegram API

Perfect for controlling your PC when you're away from your desk but still on the same network, or through Telegram from anywhere!

---

## ✨ Features

### 🖥️ System Control
- **Lock Screen** - Instantly lock your PC
- **Sleep/Suspend** - Put PC to sleep mode
- **Shutdown** - Safely shutdown (with confirmation)
- **Screenshot** - Capture and receive screenshots via Telegram

### 🔊 Media Control
- **Volume Control** - Adjust system volume (0-100%)
- **Mute/Unmute** - Toggle audio mute
- **Quick Volume Presets** - 25%, 50%, 75%, 100%

### 📋 Clipboard Sync
- **Copy to Clipboard** - Send text from Telegram to PC clipboard
- **Get Clipboard** - Retrieve current clipboard content
- **Bidirectional Sync** - Keep clipboard in sync

### 📁 File Operations
- **Upload Files** - Send files from Telegram to PC
- **Download Files** - Retrieve files from PC to Telegram
- **Photo Upload** - Save photos directly to PC
- **Document Support** - All file types supported

### 🎨 Interface Options
- **Reply Keyboard** - Persistent buttons always visible
- **Inline Keyboard** - Contextual buttons in messages
- **Text Commands** - Traditional command-based control

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TELEGRAM                              │
│                  (Cloud Service)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Long Polling
                     │
        ┌────────────▼─────────────┐
        │   Telegram Bot           │
        │   (Python - aiogram)     │
        │   Port: N/A              │
        │   - Receives messages    │
        │   - Keyboard interface   │
        │   - File handling        │
        └────────────┬─────────────┘
                     │
                     │ HTTP Requests
                     │ (localhost:5000)
                     │ Auth: Bearer Token
                     │
        ┌────────────▼─────────────┐
        │   Python Client          │
        │   (Flask Server)         │
        │   Port: 5000             │
        │   - System commands      │
        │   - File operations      │
        │   - Screenshot (scrot)   │
        └────────────┬─────────────┘
                     │
                     │ OS Commands
                     │
        ┌────────────▼─────────────┐
        │   Operating System       │
        │   (Arch Linux / Windows) │
        │   - Lock screen          │
        │   - Volume control       │
        │   - Clipboard ops        │
        └──────────────────────────┘
```

### Component Flow

1. **User** sends message/command to Telegram bot
2. **Telegram Bot** (aiogram) receives via long polling
3. Bot **validates authorization** (OWNER_ID check)
4. Bot **sends HTTP request** to local Flask server
5. **Flask server** validates auth token
6. Flask executes **OS command** (screenshot, lock, etc.)
7. Flask returns **response** to bot
8. Bot sends **result** back to user on Telegram

---

## 📦 Prerequisites

### System Requirements
- **Operating System**: Linux (Arch Linux recommended), Windows, or macOS
- **Python**: 3.9 or higher
- **Node.js** (Optional): 18+ if using Node.js bot version
- **Internet Connection**: Required for initial setup and Telegram API

### System Packages (Arch Linux)

```bash
# Screenshot tool (REQUIRED)
sudo pacman -S scrot

# Optional: Additional screenshot tools
sudo pacman -S maim imagemagick

# Volume control (REQUIRED for audio features)
sudo pacman -S alsa-utils

# Clipboard support
sudo pacman -S xclip xsel
```

### For Other Distributions

```bash
# Ubuntu/Debian
sudo apt install scrot maim imagemagick alsa-utils xclip xsel

# Fedora
sudo dnf install scrot maim ImageMagick alsa-utils xclip xsel

# macOS (via Homebrew)
brew install imagemagick
```

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/telegram-kde-bot.git
cd telegram-kde-bot
```

### 2. Install Bot (Python - aiogram)

```bash
cd bot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```
aiogram==3.13.1
aiohttp==3.9.1
python-dotenv==1.0.0
```

### 3. Install Client (Python - Flask)

```bash
cd ../client

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
psutil==5.9.6
pyperclip==1.8.2
requests==2.31.0
```

---

## ⚙️ Configuration

### 1. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. **Save your bot token**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
4. Get your user ID from [@userinfobot](https://t.me/userinfobot)

### 2. Configure Bot (.env)

Create `bot/.env`:

```bash
# Telegram Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OWNER_ID=7709438090

# Local Python Client
CLIENT_URL=http://127.0.0.1:5000
AUTH_TOKEN=your-secret-random-token-here-change-this

# Settings (optional)
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
```

**🔒 Important**: Generate a strong random token:

```bash
# Generate secure random token
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Configure Client (.env)

Create `client/.env`:

```bash
# Server Configuration
HOST=127.0.0.1
PORT=5000
AUTH_TOKEN=your-secret-random-token-here-change-this

# Storage Directories
UPLOAD_DIR=./uploads
SCREENSHOT_DIR=./screenshots
DOWNLOAD_DIR=./downloads
```

**⚠️ Critical**: `AUTH_TOKEN` must be **identical** in both files!

### 4. Create Directories

```bash
cd client
mkdir -p uploads screenshots downloads
```

---

## 🎮 Usage

### Start the System

**Terminal 1** - Start Python Client (Flask):

```bash
cd client
source venv/bin/activate
python server.py
```

Expected output:
```
============================================================
🚀 KDE Connect Bot - Python Client (Flask)
============================================================
📡 Host: 127.0.0.1
🔌 Port: 5000
🔒 Auth: ✅ ENABLED

🐛 System Info:
   OS: Linux
   Display: :0
   Session: x11
   User: zuckdorsey
============================================================

✅ Server ready at http://127.0.0.1:5000
   Waiting for bot commands...
```

**Terminal 2** - Start Telegram Bot:

```bash
cd bot
source venv/bin/activate
python bot.py
```

Expected output:
```
============================================================
🤖 Telegram KDE Connect Bot - Reply Keyboard
============================================================
👤 Owner: 7709438090
🔗 Client: http://127.0.0.1:5000
🔑 Auth: your-secre...nge-this
============================================================

📡 Starting bot with long polling...

✅ Bot started successfully!
📱 Send /start to your bot on Telegram
⌨️ Reply keyboard will appear at bottom of chat
```

### First Time Setup

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. **Reply keyboard** will appear at the bottom of the chat

---

## 📱 Commands

### Keyboard Layout

The bot uses a **persistent reply keyboard** that stays visible:

```
┌──────────────┬──────────────┐
│  🖥️ System   │  🔊 Media    │
├──────────────┼──────────────┤
│ 📋 Clipboard │  📁 Files    │
├──────────────┼──────────────┤
│  ℹ️ Status   │  ❓ Help     │
└──────────────┴──────────────┘
```

### Text Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show main menu with keyboard | `/start` |
| `/help` | Display help message | `/help` |
| `/status` | Show system information | `/status` |
| `/volume <0-100>` | Set volume level | `/volume 50` |
| `/copy <text>` | Copy text to clipboard | `/copy Hello World` |
| `/search <process>` | Search for running processes | `/search chrome` |
| `/kill <pid>` | Kill a process by PID | `/kill 1234` |
| `/confirm_shutdown` | Confirm PC shutdown | After shutdown warning |

### System Menu (🖥️ System)

```
┌──────────────┬──────────────┐
│ 🔒 Lock Screen│  😴 Sleep   │
├──────────────┼──────────────┤
│ 📸 Screenshot │ ⚠️ Shutdown │
├──────────────┴──────────────┤
│      « Main Menu            │
└─────────────────────────────┘
```

- **🔒 Lock Screen**: Instantly lock your PC
- **😴 Sleep**: Put PC into sleep/suspend mode
- **📸 Screenshot**: Capture screen and receive via Telegram
- **⚠️ Shutdown**: Shutdown PC (requires confirmation)

### Media Menu (🔊 Media)

```
┌──────────────┬──────────────┐
│  🔇 Mute     │  🔉 25%      │
├──────────────┼──────────────┤
│  🔉 50%      │  🔊 75%      │
├──────────────┼──────────────┤
│  🔊 100%     │  « Back      │
└──────────────┴──────────────┘
```

- **🔇 Mute**: Toggle system mute on/off
- **🔉/🔊 Volume**: Quick volume presets

### Clipboard Menu (📋 Clipboard)

```
┌──────────────┬──────────────┐
│ 📋 Get Clipboard │ ✍️ Copy Text │
├──────────────┴──────────────┤
│      « Main Menu            │
└─────────────────────────────┘
```

- **📋 Get Clipboard**: Retrieve current clipboard content
- **✍️ Copy Text**: Prompts you to send text to copy

### Files Menu (📁 Files)

```
┌──────────────┬──────────────┐
│ 📤 Upload File│ 📥 Download File│
├──────────────┴──────────────┤
│      « Main Menu            │
└─────────────────────────────┘
```

#### Upload Files to PC
1. Click **"📤 Upload File"** or send any file/photo directly
2. File is saved to `client/uploads/` directory
3. Bot confirms with file path

#### Download Files from PC
1. Click **"📥 Download File"**
2. Send the **full file path**, e.g.:
   - Linux: `/home/user/document.pdf`
   - Windows: `C:\Users\user\file.txt`
3. Bot sends the file to you

---

## 🎯 Features in Detail

### 📸 Screenshot System

The bot uses **scrot** for reliable screenshots on Linux:

```python
# Automatically handles:
- DISPLAY environment variable
- PNG compression
- File naming with timestamp
- Streaming to Telegram
```

**Manual screenshot test:**
```bash
# Test if scrot works
scrot /tmp/test.png && echo "✅ Success" || echo "❌ Failed"

# Set DISPLAY if needed
export DISPLAY=:0
scrot /tmp/test.png
```

### 🔊 Volume Control

Uses `amixer` on Linux:

```bash
# Set volume to 50%
amixer set Master 50%

# Mute/unmute
amixer set Master toggle
```

### 📋 Clipboard Operations

Powered by `pyperclip`:

```python
# Copy text from Telegram to PC
pyperclip.copy("Hello from Telegram")

# Get text from PC to Telegram
content = pyperclip.paste()
```

### 🔒 Security Features

1. **Owner-only access**: Only configured `OWNER_ID` can use bot
2. **Token authentication**: HTTP requests validated with `AUTH_TOKEN`
3. **Localhost only**: Flask server binds to `127.0.0.1`
4. **No external database**: All data local
5. **Confirmation dialogs**: Dangerous actions require confirmation

---

## 🐛 Troubleshooting

### Bot Won't Start

**Error**: `BOT_TOKEN is required in .env file`

**Solution**:
```bash
cd bot
cat .env  # Check if BOT_TOKEN exists
# Add BOT_TOKEN if missing
```

---

### Client Not Reachable

**Error**: `❌ Python client not running`

**Solution**:
```bash
# Check if client is running
curl http://127.0.0.1:5000/
# Should return 404 or response

# Start client
cd client
python server.py
```

---

### Screenshot Fails

**Error**: `X get_image failed: error 8`

**Solution**:

```bash
# 1. Install scrot
sudo pacman -S scrot

# 2. Test scrot manually
scrot /tmp/test.png

# 3. Check DISPLAY
echo $DISPLAY  # Should show :0 or :1

# 4. Set DISPLAY if empty
export DISPLAY=:0

# 5. Restart client
cd client
python server.py
```

---

### Authentication Failed

**Error**: `❌ Unauthorized. Check AUTH_TOKEN`

**Solution**:
```bash
# Ensure AUTH_TOKEN is identical in both files
diff bot/.env client/.env

# Should show same AUTH_TOKEN value
```

---

### Volume Control Not Working

**Error**: `amixer: command not found`

**Solution**:
```bash
# Install alsa-utils
sudo pacman -S alsa-utils

# Test amixer
amixer set Master 50%
```

---

### Port Already in Use

**Error**: `Address already in use: 5000`

**Solution**:
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or use different port in client/.env
PORT=5001
```

---

## 🔐 Security

### Best Practices

1. **Keep AUTH_TOKEN secret**: Never commit to Git
2. **Use strong tokens**: Generate with `secrets.token_urlsafe(32)`
3. **Restrict OWNER_ID**: Only your Telegram user ID
4. **Localhost only**: Never expose Flask to public internet
5. **Review commands**: Understand what each command does

### .gitignore

```gitignore
# Environment files
.env
*.env

# Virtual environments
venv/
env/
__pycache__/

# Generated files
uploads/
screenshots/
downloads/
*.pyc
*.log
```

---

## 🛠️ Development

### Project Structure

```
telegram-kde-bot/
├── bot/                          # Telegram Bot
│   ├── bot.py                    # Main bot file
│   ├── config.py                 # Configuration loader
│   ├── client.py                 # HTTP client
│   ├── keyboards.py              # Keyboard layouts (optional)
│   ├── requirements.txt
│   └── .env
│
├── client/                       # Python Local Client
│   ├── server.py                 # Flask server
│   ├── handlers/
│   │   ├── system.py            # System commands
│   │   ├── clipboard.py         # Clipboard ops
│   │   └── volume.py            # Volume control
│   ├── requirements.txt
│   └── .env
│
├── README.md
├── LICENSE
└── .gitignore
```

### Adding New Commands

**1. Add to Flask Client** (`client/server.py`):

```python
@app.route('/command', methods=['POST'])
def handle_command():
    command = request.json.get('command')
    
    if command == 'your_new_command':
        return jsonify({
            'status': 'success',
            'message': 'Command executed'
        })
```

**2. Add to Bot** (`bot/bot.py`):

```python
async def handle_new_command(message: Message):
    result = await client.send_command('your_new_command')
    await message.answer(f"✅ {result['message']}")

# Register handler
dp.message.register(handle_new_command, F.text == '🆕 New Command')
```

**3. Add to Keyboard**:

```python
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='🆕 New Command')],
        # ... existing buttons
    ])
    return keyboard
```

### Testing

```bash
# Test screenshot method
cd client
python test_screenshot.py

# Test HTTP endpoint
curl -X POST http://127.0.0.1:5000/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"command": "status"}'

# Test bot locally
cd bot
python bot.py
# Send /start to bot
```

---

## 📊 System Requirements

### Minimum

- **RAM**: 256MB (bot) + 512MB (client)
- **CPU**: Any modern CPU (minimal usage)
- **Storage**: 100MB for code + space for uploads
- **Network**: Internet for Telegram API

### Recommended

- **RAM**: 512MB (bot) + 1GB (client)
- **CPU**: Dual-core or better
- **Storage**: 1GB free space
- **Network**: Stable internet connection

---

## 🚀 Performance

- **Bot response time**: < 100ms (local network)
- **Screenshot capture**: 1-3 seconds
- **File upload**: Depends on file size and network
- **System commands**: Instant (< 50ms)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 zuckdorsey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **Telegram Bot API** - For the amazing bot platform
- **aiogram** - Modern Python async Telegram bot framework
- **Flask** - Lightweight Python web framework
- **scrot** - Reliable screenshot utility for X11
- **KDE Connect** - Original inspiration

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/telegram-kde-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/telegram-kde-bot/discussions)
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Media player control (play/pause/next)
- [ ] Battery status monitoring
- [ ] Network information
- [ ] Process manager (list/kill processes)

### Version 1.2 (Planned)
- [ ] Custom command execution
- [ ] Scheduled tasks
- [ ] Multi-language support
- [ ] Web dashboard

### Version 2.0 (Future)
- [ ] Mobile app notifications
- [ ] Cloud sync option
- [ ] Multi-PC support
- [ ] Plugin system

---

## ❓ FAQ

### Q: Is this safe to use?

**A**: Yes, when configured properly. The bot only responds to your Telegram user ID, communication is authenticated, and the Flask server only listens on localhost.

### Q: Can I use this from outside my home network?

**A**: Yes! As long as your PC is on and connected to the internet, you can control it from anywhere via Telegram.

### Q: Does this work on Windows/macOS?

**A**: Yes, with minor adjustments:
- Windows: Some system commands differ (no scrot, use different lock command)
- macOS: Similar to Linux but uses macOS-specific commands

### Q: How much data does it use?

**A**: Minimal - mostly text messages. Screenshots use bandwidth based on resolution.

### Q: Can multiple users control the same PC?

**A**: No, by design it's single-user. You can modify the code to add multiple `OWNER_ID` values if needed.

### Q: What if I lose internet connection?

**A**: The bot won't work without internet (needs Telegram API), but the Flask server continues running locally.

---

## 📸 Screenshots

### Main Menu
```
🤖 KDE Connect Bot

Control your PC from Telegram!

[🖥️ System] [🔊 Media]
[📋 Clipboard] [📁 Files]
[ℹ️ Status] [❓ Help]
```

### System Status
```
✅ System Online

🖥️ Host: arch-pc
💻 OS: Linux 6.6.8-arch1-1
📊 CPU: 15.3%
💾 RAM: 42.7%
⏱️ Uptime: 5h 23m
```

### Screenshot Feature
```
📸 Taking screenshot...

[Image appears in chat]

📸 Screenshot
```

---

## 🎉 Quick Start Summary

```bash
# 1. Install scrot
sudo pacman -S scrot

# 2. Clone repo
git clone https://github.com/yourusername/telegram-kde-bot.git
cd telegram-kde-bot

# 3. Setup bot
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env with BOT_TOKEN, OWNER_ID, AUTH_TOKEN

# 4. Setup client
cd ../client
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env with same AUTH_TOKEN

# 5. Run (in separate terminals)
cd client && python server.py
cd bot && python bot.py

# 6. Send /start to your bot on Telegram!
```

---

**Built with ❤️ for personal PC control via Telegram**

**Star ⭐ this repo if you find it useful!**
