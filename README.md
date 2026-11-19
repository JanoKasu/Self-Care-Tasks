# Self Care Tasks

A PySide6/QML self-care dashboard designed for a Raspberry Pi touchscreen.

## Gamification

Completing a task earns 10 XP for low-impact tasks, 20 XP for medium-impact
tasks, or 30 XP for high-impact tasks. Each task can earn XP once per scheduled
occurrence, and every 100 XP unlocks the next level. XP is stored with the app
data and is preserved when the 30-day completion history is cleaned up.

Tasks can be scheduled daily, weekly, or monthly, independently of priority.
The Progress tab summarizes level, XP, streaks, and schedule completion. The
Needs Attention tab lists recurring tasks with missed daily or weekly
occurrences.

Completed daily tasks reset at local midnight. Weekly tasks remain checked
until the next Monday, and monthly tasks remain checked until the first day of
the next month. The next reset is scheduled automatically and expired tasks
are also corrected immediately when the app starts.

Task cards use a priority gradient: red for high priority, green for medium
priority, and gold for low priority.

## Weather

The Weather tab shows current conditions, the next eight hours, and a
seven-day forecast. Choose a city once with the touchscreen search interface;
the coordinates are saved in `data/weather.json` and the forecast refreshes
every 15 minutes while the app is open. Forecasts use Open-Meteo and are shown
in Fahrenheit. An internet outage is reported on the page without blocking the
rest of the dashboard.

The dashboard switches to its dark theme automatically from 8:00 PM until
6:00 AM, using the device's local time. It schedules a timer for the next
switch and emits `Theme.themeChanged(darkMode)` when the mode changes.

## Install on Raspberry Pi OS

```bash
cd "$HOME/Documents/Self-Care-Tasks"
sudo apt update
sudo apt install -y python3-venv python3-pip \
  libegl1 libgl1 libgbm1 libxkbcommon0 libxcb-cursor0 \
  libxcb-xinerama0 libnss3 libasound2 x11-xserver-utils

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

## Data storage and backups

The dashboard stores its SQLite database at `data/dashboard.db`. This directory
is ignored by Git, so code updates and ordinary Git operations do not overwrite
your tasks, completion history, or XP.

To keep data outside the source checkout, set `SELF_CARE_DATA_DIR` in the
autostart command:

```ini
Exec=env SELF_CARE_DATA_DIR=/home/janokasu/.local/share/self-care-tasks /home/janokasu/Documents/Self-Care-Tasks/.venv/bin/python /home/janokasu/Documents/Self-Care-Tasks/main.py
```

On each normal startup the app:

1. verifies the database with SQLite's quick integrity check;
2. refreshes `dashboard.db.backup` with a transactionally consistent copy;
3. applies any pending schema migration;
4. keeps SQLite write-ahead logging and foreign-key enforcement enabled.

Copy the database directory to external storage regularly for off-device
backups. To restore the last automatic backup, close the dashboard, copy
`dashboard.db.backup` over `dashboard.db`, and reopen the app. Move the original
corrupted database elsewhere rather than deleting it if recovery is needed.

Do not edit the database while the app is running. If startup reports an
integrity error, restore a known-good backup before reopening it.

## Development and tests

```bash
.venv/bin/python -m unittest discover -s tests
```

Tests use isolated temporary databases and cover task persistence, completion
periods, XP, migrations, backups, navigation, inactivity, and application
updates. The update controller tests mock Git and pip so test runs never modify
the checkout or install packages.

## Update

Click the refresh button at the bottom of the navigation bar. The dashboard
checks the tracked Git branch, downloads a fast-forward-only update, refreshes
Python dependencies if `requirements.txt` changed, and then offers to restart.
Your ignored `data/dashboard.db` file is not changed.

Automatic updates require a clean checkout. Commit, stash, or discard tracked
local changes before using the update button.

For a command-line update, close the running application and run:

```bash
cd "$HOME/Documents/Self-Care-Tasks"
git pull
.venv/bin/python -m pip install -r requirements.txt
```

No application rebuild or repackaging is required; the dashboard runs directly
from this checkout.
