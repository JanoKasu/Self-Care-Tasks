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

## Run from source on Raspberry Pi OS

```bash
cd "$HOME/Documents/Self-Care-Tasks"
sudo apt update
sudo apt install -y python3-venv python3-pip \
  libegl1 libgl1 libgbm1 libxkbcommon0 libxcb-cursor0 \
  libxcb-xinerama0 libnss3 libasound2 x11-xserver-utils network-manager

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Run the application while logged into the Raspberry Pi desktop. Do not use
`sudo`, because the app stores its data in the current user's home directory.

## Build an AppImage

Build on a 64-bit Raspberry Pi or another ARM64 Linux machine. The generated
binary must match the Pi's architecture and Linux libraries.

```bash
cd "$HOME/Documents/Self-Care-Tasks"
chmod +x scripts/build-appimage.sh
./scripts/build-appimage.sh
```

The first build installs Python packages and downloads the architecture-specific
`appimagetool`. The finished file is named
`Self_Care_Tasks-aarch64.AppImage` (the architecture can vary).

To run it from the desktop:

```bash
chmod +x Self_Care_Tasks-aarch64.AppImage
./Self_Care_Tasks-aarch64.AppImage
```

You can also right-click the AppImage in the file manager, select **Properties**
then **Permissions**, enable **Allow executing file as program**, and double-click
it. The app stores its database at
`~/.local/share/self-care-tasks/dashboard.db`.

## Deploy a new version to the Pi

The instructions below update the repository, rebuild the AppImage, and replace
the extracted copy used by `AppRun`. Close the running application first.

```bash
cd "$HOME/Documents/Self-Care-Tasks"
git pull
./scripts/build-appimage.sh
```

If running the AppImage directly works on the Pi, replace the old executable
and launch the new one:

```bash
chmod +x Self_Care_Tasks-aarch64.AppImage
./Self_Care_Tasks-aarch64.AppImage
```

If the Pi reports that FUSE is unavailable, deploy and extract the AppImage as
follows. Replace `aarch64` in the filename if the build used a different
architecture:

```bash
mkdir -p "$HOME/Applications/SelfCareTasks"
cp -f Self_Care_Tasks-aarch64.AppImage \
  "$HOME/Applications/SelfCareTasks/"

cd "$HOME/Applications/SelfCareTasks"
rm -rf squashfs-root
chmod +x Self_Care_Tasks-aarch64.AppImage
./Self_Care_Tasks-aarch64.AppImage --appimage-extract
./squashfs-root/AppRun
```

Use that last command for later launches:

```bash
"$HOME/Applications/SelfCareTasks/squashfs-root/AppRun"
```

The extracted deployment can be reopened through the file manager by opening
`AppRun` inside
`~/Applications/SelfCareTasks/squashfs-root/`. Do not open the `.AppImage`
with Archiver.

Rebuilding or replacing the application does not delete user data. The task
database remains at
`~/.local/share/self-care-tasks/dashboard.db`.
