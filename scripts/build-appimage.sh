#!/usr/bin/env bash

set -euo pipefail

project_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "Build the Raspberry Pi AppImage from Linux, ideally on the target Pi." >&2
    exit 1
fi

case "$(uname -m)" in
    aarch64|arm64)
        appimagetool_arch="aarch64"
        ;;
    armv7l)
        appimagetool_arch="armhf"
        ;;
    x86_64)
        appimagetool_arch="x86_64"
        ;;
    *)
        echo "Unsupported architecture: $(uname -m)" >&2
        exit 1
        ;;
esac

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-build.txt

rm -rf build/appimage build/pyinstaller
mkdir -p build/appimage/AppDir/usr/bin

python -m PyInstaller \
    --clean \
    --noconfirm \
    --onedir \
    --windowed \
    --name self-care-tasks \
    --distpath build/pyinstaller \
    --workpath build/pyinstaller-work \
    --specpath build \
    --collect-all PySide6 \
    --add-data "$project_dir/qml:qml" \
    main.py

cp -a build/pyinstaller/self-care-tasks/. \
    build/appimage/AppDir/usr/bin/
cp packaging/AppRun build/appimage/AppDir/AppRun
cp packaging/self-care-tasks.desktop \
    build/appimage/AppDir/self-care-tasks.desktop
cp packaging/self-care-tasks.svg \
    build/appimage/AppDir/self-care-tasks.svg
chmod +x \
    build/appimage/AppDir/AppRun \
    build/appimage/AppDir/usr/bin/self-care-tasks

appimagetool="build/appimagetool-${appimagetool_arch}.AppImage"
if [[ ! -x "$appimagetool" ]]; then
    curl --fail --location \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${appimagetool_arch}.AppImage" \
        --output "$appimagetool"
    chmod +x "$appimagetool"
fi

export APPIMAGE_EXTRACT_AND_RUN=1
"$appimagetool" \
    build/appimage/AppDir \
    "Self_Care_Tasks-$(uname -m).AppImage"

echo
echo "Created: $project_dir/Self_Care_Tasks-$(uname -m).AppImage"
