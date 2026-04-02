import os
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from messages import LOVE_MESSAGES

import requests



STATE_FILE = Path("/app/state.json")


def load_env_file(env_path=".env"):
    env_file = Path(env_path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        # Do not override existing environment vars (e.g., from Docker/K8s secret injection)
        if key and os.getenv(key) is None:
            os.environ[key] = value


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def choose_message(messages, last_message=None):
    if len(messages) == 1:
        return messages[0]
    pool = [m for m in messages if m != last_message]
    return random.choice(pool if pool else messages)

def random_time_for_day(base_date):
    hour = random.randint(7, 18)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=second, microsecond=0)

def send_nextcloud_talk_message(message):
    # Grab the variables and strip out any accidental quotes
    url_base = os.getenv("NEXTCLOUD_URL", "").strip('"').rstrip("/")
    user = os.getenv("NEXTCLOUD_USER", "").strip('"')
    password = os.getenv("NEXTCLOUD_APP_PASSWORD", "").strip('"')
    token = os.getenv("NEXTCLOUD_CHAT_TOKEN", "").strip('"')

    missing = [x for x in ["NEXTCLOUD_URL", "NEXTCLOUD_USER", "NEXTCLOUD_APP_PASSWORD", "NEXTCLOUD_CHAT_TOKEN"] if not os.getenv(x)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables for Nextcloud Talk: {', '.join(missing)}. "
            "Please set them in the .env file or environment before starting the service."
        )

    url = f"{url_base}/ocs/v2.php/apps/spreed/api/v1/chat/{token}"

    headers = {
        "OCS-APIRequest": "true",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"message": message}

    print(f"DEBUG: Attempting to send to {url} as user {user}")

    resp = requests.post(
        url,
        headers=headers,
        json=payload,
        auth=(user, password),
        timeout=30,
    )
    resp.raise_for_status()
    return resp

def ensure_today_schedule(state):
    today = datetime.now().date().isoformat()
    if state.get("scheduled_date") != today:
        target = random_time_for_day(datetime.now())
        state["scheduled_date"] = today
        state["scheduled_time"] = target.isoformat()
        state["sent"] = False
        save_state(state)
        print(f"[*] New schedule generated for today: {target.isoformat()}")
    return datetime.fromisoformat(state["scheduled_time"])

def main():
    print("Bot starting up...")

    # Read environment from .env if present (not committed to GitHub)
    load_env_file()

    state = load_state()

    while True:
        now = datetime.now()
        target = ensure_today_schedule(state)

        if not state.get("sent", False) and now >= target:
            message = choose_message(LOVE_MESSAGES, state.get("last_message"))
            try:
                send_nextcloud_talk_message(message)
                state["sent"] = True
                state["last_message"] = message
                state["last_sent_at"] = now.isoformat()
                save_state(state)
                print(f"[OK] Sent message successfully at {now.isoformat()}")
            except Exception as e:
                print(f"[ERROR] Failed to send at {now.isoformat()}: {e}")

        # Reset for the next day
        if state.get("scheduled_date") != datetime.now().date().isoformat():
            state["sent"] = False
            save_state(state)

        time.sleep(30)

if __name__ == "__main__":
    main()