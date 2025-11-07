# AI agent guide for KDE-BOT

Purpose: help an AI coding agent be productive immediately in this repo by capturing the real architecture, conventions, and gotchas.

## Big picture

- Two local components on the same machine:
  - Telegram bot (Python, aiogram) in `bot/` — UI via Reply Keyboard, long polling.
  - Local client (Python, Flask) in `client/` — executes OS-level actions. Auth via Bearer token.
- Flow: Telegram -> `bot/bot.py` handlers -> `bot/client.SystemClient` HTTP -> `client/server.py` `/command` dispatcher -> OS commands -> JSON back to bot.
- Single-user by design: only `OWNER_ID` is authorized at the bot layer; Flask enforces `AUTH_TOKEN`.

## Key files and roles

- `bot/bot.py`: main entry. Uses Reply Keyboard (not inline), registers message handlers, applies `ErrorMiddleware`, and enforces owner auth (`authorize`). Uses `CommandManager.run_exclusive(...)` to cancel previous in-flight tasks per chat.
- `bot/client.py` (`SystemClient`): async HTTP client with retries/backoff and consistent error messages. All requests include `Authorization: Bearer <AUTH_TOKEN>`.
- `bot/command_manager.py`: per-chat exclusivity for commands; always wrap long-running tasks with it to avoid duplicate work.
- `bot/utils.py`: safe message edits/deletes, `chat_action` context, and `result_icon` helper.
- `client/server.py`: Flask app. Endpoints: `/` (health), `/status`, `/command` (switch on `command`), `/upload`, `/getfile`, `/download/<filename>`.
  - Command names implemented today: `lock`, `volume`, `mute`, `copy`, `paste`, `screenshot` (Linux), `sleep`, `shutdown`, `battery_status`, `network_info`, `network_stats`.
  - Security: `require_auth` checks Bearer token; server binds to `HOST` (default 127.0.0.1).
  - File download is restricted to `ALLOWED_DOWNLOAD_DIRS` (defaults to `uploads/` and `screenshots/`).
- Legacy/alt UI: `bot/handlers/*` and `bot/keyboards.py` implement an inline-keyboard flow not used by `bot/bot.py`. Current UI is the Reply Keyboard in `bot/bot.py`; unknown callbacks are handled by `bot/fallbacks.py` to redirect users to `/start`.

## Configuration and running

- Both sides use dotenv. Create `bot/.env` and `client/.env`; `AUTH_TOKEN` must match exactly.
  - Bot: `BOT_TOKEN`, `OWNER_ID`, `CLIENT_URL`, `AUTH_TOKEN`, optional `LOG_LEVEL`, `REQUEST_TIMEOUT`.
  - Client: `HOST`, `PORT`, `AUTH_TOKEN`, `UPLOAD_DIR`, `SCREENSHOT_DIR`.
- First run requires system packages for features used by `client/server.py`:
  - Linux: `scrot` (screenshots), `alsa-utils` (volume), `xclip`/`xsel` (clipboard), plus Python deps from each `requirements.txt`.
- Typical dev loop: start Flask client first (`client/server.py`), then the bot (`bot/bot.py`). The bot will surface clear errors if the client is down (from `SystemClient`).

## Implementation patterns that matter here

- Bot auth and exclusivity:
  - Always gate handlers with `authorize(message)` as in `bot/bot.py` to enforce `OWNER_ID`.
  - For actions that can be spammed or take time (screenshot, sleep, volume), wrap the work in `CommandManager.run_exclusive(chat_id=..., coro_factory=..., on_cancel=...)`.
- Bot-to-client contract:
  - POST `/command` with JSON `{ "command": "<name>", "params": { ... } }` and expect JSON `{ status: "success"|"error", message: string, ... }`.
  - Example implemented calls in bot: `client.send_command('screenshot')`, `client.send_command('volume', { 'level': 50 })`.
- Client command handler:
  - Add cases inside `execute_command(command, params)` and return the standard JSON shape above.
  - Keep OS-specific branches (Linux/Windows/macOS) together like the existing commands.
- Messaging UX:
  - Prefer Reply Keyboard buttons in `bot/bot.py` (`main_keyboard`, `system_keyboard`, etc.). Make text matches exact labels, e.g. `'🔒 Lock Screen'`.
  - Use `utils.safe_edit`/`safe_delete` to avoid Telegram edit/delete errors, and `chat_action` to show typing/upload indicators.

## Gotchas and guardrails

- AUTH is mandatory in both layers: missing or mismatched `AUTH_TOKEN` yields 401 from Flask; `SystemClient` surfaces helpful messages (e.g., "Python client not running...").
- Screenshots on Linux need a valid `DISPLAY`; server defaults to `:0` if missing, but ensure X session is available; `scrot` must be installed.
- File download via `/getfile` is limited to `uploads/` and `screenshots/` by default; tests outside those paths will 403.
- Some inline handlers reference commands like `process_*` or `media_*` that are not currently implemented in `client/server.py`. Either implement them under `/command` or avoid wiring those routes when using the Reply Keyboard UI.

## Adding a new feature (concrete example)

- Client (`client/server.py`):
  - Inside `execute_command`, add:
    - `elif command == 'reboot':` run the appropriate OS command and `return { 'status': 'success', 'message': '🔁 Rebooting...' }`.
- Bot (`bot/bot.py`):
  - Add a button label (e.g., `'🔁 Reboot'`) in the appropriate keyboard, register a handler with an `authorize` check, and inside a `run_exclusive(...)` call `client.send_command('reboot')` then edit the message using `result_icon`.

## When in doubt

- Follow the patterns in `bot/bot.py` and `client/server.py`; keep the JSON contract and auth behavior consistent.
- Prefer the Reply Keyboard path and exclusive command manager; treat the inline keyboard router files as legacy/optional.
- Keep OS commands inside the Flask side; the bot should remain async/IO-only.
