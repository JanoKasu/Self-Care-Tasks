# Self Care Tasks

A PySide6/QML self-care dashboard designed for a Raspberry Pi touchscreen.

## Gamification

Completing a task earns 10 XP for low-impact tasks, 20 XP for medium-impact
tasks, or 30 XP for high-impact tasks. Each task can earn XP once per scheduled
occurrence, and every 100 XP unlocks the next level. XP is stored with the app
data and is preserved when the 30-day completion history is cleaned up.

Tasks can be scheduled daily, weekly, or as needed, independently of priority.
The Progress tab summarizes level, XP, streaks, and schedule completion. The
Needs Attention tab lists recurring tasks with missed daily or weekly
occurrences.

## Install on Raspberry Pi OS

```bash
cd "$HOME/Documents/Self-Care-Tasks"
sudo apt update
sudo apt install -y python3-venv python3-pip \
  libegl1 libgl1 libgbm1 libxkbcommon0 libxcb-cursor0 \
  libxcb-xinerama0 libnss3 libasound2 x11-xserver-utils network-manager

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Run

Run the application while logged into the Raspberry Pi desktop:

```bash
cd "$HOME/Documents/Self-Care-Tasks"
.venv/bin/python main.py
```

Do not use `sudo`, because the app stores its database in the repository's
ignored `data/dashboard.db` file.

## Autostart

Create `~/.config/autostart/self-care-dashboard.desktop` with the following
contents:

```ini
[Desktop Entry]
Type=Application
Name=Self_Care_Dashboard
Path=/home/janokasu/Documents/Self-Care-Tasks
Exec=/home/janokasu/Documents/Self-Care-Tasks/.venv/bin/python /home/janokasu/Documents/Self-Care-Tasks/main.py
Terminal=false
X-GNOME-Autostart-enabled=true
```

If the repository is in a different location, replace both occurrences of
`/home/janokasu/Documents/Self-Care-Tasks` with its absolute path. Keep the
path to `.venv/bin/python` absolute so autostart does not depend on shell
activation or `PATH`.

## Update

Close the running application before updating:

```bash
cd "$HOME/Documents/Self-Care-Tasks"
git pull
.venv/bin/python -m pip install -r requirements.txt
```

Updating the repository does not delete `data/dashboard.db`.
