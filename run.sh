#!/usr/bin/env bash
# GitHub Copilot
# run.sh - simple runner for KDE-BOT (starts client then bot, with venvs & logs)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/logs"
VENV_CLIENT="$ROOT/.venv_client"
VENV_BOT="$ROOT/.venv_bot"
CLIENT_PID_FILE="$ROOT/.client.pid"
BOT_PID_FILE="$ROOT/.bot.pid"

mkdir -p "$LOG_DIR"

cleanup() {
    echo "Shutting down..."
    [ -f "$CLIENT_PID_FILE" ] && kill "$(cat "$CLIENT_PID_FILE")" 2>/dev/null || true
    [ -f "$BOT_PID_FILE" ] && kill "$(cat "$BOT_PID_FILE")" 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM EXIT

ensure_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        echo "python3 is required but not found. Aborting."
        exit 1
    fi
    if ! command -v pip3 >/dev/null 2>&1; then
        echo "pip3 is required but not found. Aborting."
        exit 1
    fi
}

create_venv_and_install() {
    local path="$1"
    local req="$2"
    if [ ! -d "$path" ]; then
        echo "Creating venv at $path"
        python3 -m venv "$path"
    fi
    # Install requirements if present
    if [ -f "$req" ]; then
        # avoid reinstalling every run by using a simple marker file
        local marker="$path/.requirements_installed"
        if [ ! -f "$marker" ]; then
            echo "Installing dependencies from $req"
            "$path/bin/pip" install --upgrade pip >/dev/null
            "$path/bin/pip" install -r "$req"
            touch "$marker"
        fi
    fi
}

# wait for HTTP endpoint
wait_for_http() {
    local url="$1"
    local tries=0
    local max=30
    until curl -sSf "$url" >/dev/null 2>&1; do
        tries=$((tries+1))
        if [ "$tries" -ge "$max" ]; then
            echo "Timeout waiting for $url"
            return 1
        fi
        echo "Waiting for $url ..."
        sleep 1
    done
    return 0
}

ensure_python

# prepare venvs
create_venv_and_install "$VENV_CLIENT" "$ROOT/client/requirements.txt"
create_venv_and_install "$VENV_BOT" "$ROOT/bot/requirements.txt"

# Start Flask client first
echo "Starting client..."
(
    cd "$ROOT" || exit 1
    # Export client env vars in a subshell to avoid polluting the runner
    set -a
    [ -f client/.env ] && . client/.env
    set +a
    # Use venv python to run server
    nohup "$VENV_CLIENT/bin/python" client/server.py >> "$LOG_DIR/client.log" 2>&1 &
    echo $! > "$CLIENT_PID_FILE"
)
# Determine health URL (prefer client/.env HOST/PORT, fall back to defaults)
# Try using client/.env values without leaving current shell
CLIENT_HOST="127.0.0.1"
CLIENT_PORT="5000"
if [ -f client/.env ]; then
    # crude parse, works for simple VAR=VALUE lines
    CLIENT_HOST="$(grep -E '^HOST=' client/.env 2>/dev/null | head -n1 | cut -d= -f2- | tr -d '\r' | tr -d '"' || true)"
    CLIENT_PORT="$(grep -E '^PORT=' client/.env 2>/dev/null | head -n1 | cut -d= -f2- | tr -d '\r' | tr -d '"' || true)"
fi
CLIENT_HOST="${CLIENT_HOST:-127.0.0.1}"
CLIENT_PORT="${CLIENT_PORT:-5000}"
HEALTH_URL="http://$CLIENT_HOST:$CLIENT_PORT/"

if ! wait_for_http "$HEALTH_URL"; then
    echo "Client did not become healthy. Check $LOG_DIR/client.log"
    exit 1
fi
echo "Client is up."

# Start bot
echo "Starting bot..."
(
    cd "$ROOT" || exit 1
    set -a
    [ -f bot/.env ] && . bot/.env
    set +a
    nohup "$VENV_BOT/bin/python" bot/bot.py >> "$LOG_DIR/bot.log" 2>&1 &
    echo $! > "$BOT_PID_FILE"
)

sleep 1
echo "Both processes started. Logs:"
echo " - client: $LOG_DIR/client.log"
echo " - bot:    $LOG_DIR/bot.log"
echo "To stop, press Ctrl+C (this script will forward SIG and stop child processes)."

# Keep script running to maintain trap and allow Ctrl+C to stop services
while true; do
    sleep 60 &
    wait $!
done