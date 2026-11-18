#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
launcher="$project_dir/scripts/start.sh"
config_dir="${XDG_CONFIG_HOME:-${HOME:?HOME must be set}/.config}"
autostart_dir="$config_dir/autostart"
desktop_file="$autostart_dir/self-care-tasks.desktop"

if [ "${1:-}" = "--uninstall" ]; then
    rm -f "$desktop_file"
    echo "Removed $desktop_file"
    exit 0
fi

if [ "${1:-}" != "" ]; then
    echo "Usage: $0 [--uninstall]" >&2
    exit 2
fi

if [ ! -x "$project_dir/.venv/bin/python" ]; then
    echo "Missing virtual environment at $project_dir/.venv" >&2
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

chmod +x "$launcher"
mkdir -p "$autostart_dir"

escaped_launcher=$(
    printf '%s' "$launcher" |
        sed 's/\\/\\\\/g; s/"/\\"/g'
)

cat > "$desktop_file" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Self Care Tasks
Comment=Launch the Self Care Tasks touchscreen interface
Exec="$escaped_launcher"
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

echo "Installed $desktop_file"
echo "The app will open fullscreen after the desktop session starts."
