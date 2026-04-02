# 💌 Love Messages Bot

A heartfelt, automated bot that sends a **randomized love message** once a day — at a random time — to your partner through **Nextcloud Talk**. Built with Python and Docker, it runs 24/7 in the background so you never forget to express how you feel.

---

## 🌹 What Does It Do?

Every single day, at a **randomly chosen time between 7:00 AM and 6:59 PM**, the bot picks one of **500+ unique, hand-crafted love messages** and sends it directly to a Nextcloud Talk chat room.

The messages celebrate your partner's kindness, patience, warmth, smile, strength, presence, and many other qualities. Each message feels personal and heartfelt — never robotic or repetitive.

Key behaviors:
- ✅ Sends **exactly one message per day** — no more, no less.
- 🎲 The **time is randomized** each day so it feels natural and spontaneous.
- 🔁 **Never repeats the same message twice in a row** — always picks something fresh.
- 💾 Remembers what it has already done using a lightweight JSON state file.
- 🐳 Runs as a **Docker container** that restarts automatically if the server reboots.

---

## 📁 Project Structure

```
love-messages-bot/
│
├── bot.py               # The main bot logic — scheduling, state, and sending
├── messages.py          # The full library of 500+ love messages
├── Dockerfile           # Builds the Python Docker image
├── docker-compose.yml   # Defines and runs the container service
├── .env                 # ⚠️ Your private credentials (NOT committed to Git)
├── state.json           # ⚠️ Runtime state file (NOT committed to Git)
└── .gitignore           # Excludes .env and state.json from version control
```

---

## ⚙️ How It Works — Step by Step

### 1. Startup
When the container starts, `bot.py` runs continuously in a loop. Every **30 seconds**, it checks:

- Has a scheduled time been set for today? If not, it picks a random hour/minute/second between 7:00 AM and 6:59 PM and saves it.
- Is it past the scheduled time? If yes, and the message hasn't been sent yet, it sends one.

### 2. Message Selection
The bot imports the entire `LOVE_MESSAGES` list from `messages.py` — over 500 messages. It picks one at random, but **excludes the last sent message** to avoid repetition. The chosen message and timestamp are saved to `state.json`.

### 3. Sending via Nextcloud Talk
The bot uses the **Nextcloud Talk REST API** (`/ocs/v2.php/apps/spreed/api/v1/chat/{token}`) to post the message to a specific chat room. Authentication is done via HTTP Basic Auth using a Nextcloud username and app password.

### 4. Daily Reset
After midnight, the bot detects that `scheduled_date` in the state file no longer matches today's date, clears the `sent` flag, and schedules a fresh random time for the new day.

---

## 🚀 Getting Started

### Prerequisites
- A server or machine running **Docker** and **Docker Compose**
- A **Nextcloud** instance with the Spreed/Talk app enabled
- A Nextcloud **App Password** (different from your account password — generate one in Nextcloud Settings → Security)
- The **token** of the Talk chat room you want to send messages to (visible in the room URL)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/HassanElwany/love-messages-bot.git
cd love-messages-bot
```

---

### Step 2 — Create the `.env` File

Create a file called `.env` in the project root with your Nextcloud credentials:

```env
NEXTCLOUD_URL=https://your-nextcloud-server.com
NEXTCLOUD_USER=your_username
NEXTCLOUD_APP_PASSWORD=your_app_password_here
NEXTCLOUD_CHAT_TOKEN=abc123xyz
```

> ⚠️ **Never commit this file.** It is already listed in `.gitignore`.

| Variable                | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `NEXTCLOUD_URL`         | The full base URL of your Nextcloud server (no trailing slash)              |
| `NEXTCLOUD_USER`        | Your Nextcloud username                                                     |
| `NEXTCLOUD_APP_PASSWORD`| An App Password generated in Nextcloud → Settings → Security               |
| `NEXTCLOUD_CHAT_TOKEN`  | The unique token for the Talk conversation (found in the chat room URL)     |

---

### Step 3 — Set Up the Docker Network

This project connects to an **external Docker network** called `comp_hs`. If you already have Nextcloud running in Docker on the same network, use the same one. Otherwise, create it:

```bash
docker network create comp_hs
```

If you want to use a different network name, edit the `networks` section in `docker-compose.yml`.

---

### Step 4 — Build and Run

```bash
docker compose up -d --build
```

This will:
- Build the Docker image using `Dockerfile`
- Start the `love-bot` container in detached mode
- Configure it to **restart automatically** (`restart: unless-stopped`) if the server reboots

---

### Step 5 — Verify It's Running

```bash
docker logs love-bot
```

You should see output like:
```
Bot starting up...
[*] New schedule generated for today: 2026-04-02T14:37:22
```

And later, when the message is sent:
```
[OK] Sent message successfully at 2026-04-02T14:37:22.123456
```

---

## 🛠️ Configuration Details

### Timezone
The container is configured to run in **Asia/Riyadh** timezone by default. To change it, edit the `TZ` environment variable in `docker-compose.yml`:

```yaml
environment:
  - TZ=Europe/London
```

### Message Time Window
By default, messages are sent between **7:00 AM and 6:59 PM**. To change this range, edit the `random_time_for_day()` function in `bot.py`:

```python
def random_time_for_day(base_date):
    hour = random.randint(7, 18)   # Change 7 and 18 to your preferred range
    ...
```

### Check Interval
The bot checks whether it's time to send a message every **30 seconds**. You can adjust this in `bot.py`:

```python
time.sleep(30)  # Change to any value in seconds
```

---

## 📨 The Message Library (`messages.py`)

The `messages.py` file contains a single Python list called `LOVE_MESSAGES` with **501 messages** covering a wide range of warm, sincere themes:

| Theme Group | Examples |
|---|---|
| **Qualities celebrated** | Kindness, patience, warmth, smile, strength, calm heart, honest heart, gentle voice, caring nature, presence |
| **Opening styles** | "My love, …", "Habibti, …", "Good morning, my love, …", "Tonight I just want to say, …" |
| **Message styles** | Daily affirmations, morning reflections, evening gratitude, heartfelt promises |
| **Closing sentiments** | "I love you deeply", "You are my peace", "I would choose you again and again", "You are still my favorite hello" |

Messages are carefully written to feel warm, non-repetitive, and genuine — not auto-generated filler. The bot's selection algorithm ensures the same message is never sent two days in a row.

---

## 💾 State File (`state.json`)

The bot uses a `state.json` file (stored inside the container at `/app/state.json` and mounted to `./state.json` on the host) to persist its state. An example:

```json
{
  "scheduled_date": "2026-04-02",
  "scheduled_time": "2026-04-02T14:37:22",
  "sent": true,
  "last_message": "My love, your kindness makes me love you more every day. I love you deeply.",
  "last_sent_at": "2026-04-02T14:37:22.123456"
}
```

> This file is **automatically excluded from Git** via `.gitignore`.

---


## 🧰 Environment Variable Priority

The `load_env_file()` function reads variables from `.env`, but **does NOT override** variables that are already set in the environment (e.g., injected by Docker secrets or a container orchestrator like Kubernetes or Portainer). This means you can safely inject secrets via your infrastructure without the `.env` file interfering.

---

## 🐳 Docker Details

| File | Purpose |
|------|---------|
| `Dockerfile` | Uses `python:3.11-slim`, installs the `requests` library, copies the bot files, and runs `bot.py` |
| `docker-compose.yml` | Defines the `love-bot` service with `restart: unless-stopped`, the `Asia/Riyadh` timezone, the `.env` file, and the state file volume mount |

---

## 🛑 Stopping the Bot

```bash
docker compose down
```

To stop without removing the container:
```bash
docker compose stop
```

---

## 🧪 Testing

To test locally without Docker, make sure you have Python 3.11+ and the `requests` library:

```bash
pip install requests
```

Create a `.env` file with your credentials, then run:

```bash
python bot.py
```

The bot will start and print its scheduled time. You can temporarily change the `random_time_for_day()` function to return `datetime.now()` to trigger an immediate send.

---

## ❤️ Made with Love

This bot was built with a simple purpose: to make someone feel loved and seen, every single day, without fail. Sometimes the most meaningful things are the simplest ones — a small message that says *"I was thinking about you."*

---

## 📄 License

This project is personal and open. Feel free to fork it and customize the messages for your own partner. ❤️
