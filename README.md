# Self Care Tasks

A PySide6/QML self-care dashboard designed for a Raspberry Pi touchscreen.

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

## Update

```bash
cd "$HOME/Documents/Self-Care-Tasks"
git pull
./scripts/build-appimage.sh
```
