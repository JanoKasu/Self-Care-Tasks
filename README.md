# Self Care Tasks

A touchscreen self-care dashboard built with Python and PySide6.

## Raspberry Pi setup

1. Configure Raspberry Pi OS to automatically log in to the desktop. In
   `sudo raspi-config`, select **System Options** > **Boot / Auto Login** >
   **Desktop Autologin**.
2. Create a virtual environment and install the project from the repository
   directory:

   ```sh
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

3. Install the desktop autostart entry:

   ```sh
   sh scripts/install-autostart.sh
   ```

4. Reboot the Pi. The app starts in fullscreen after the graphical desktop
   session opens.

The installer adds
`~/.config/autostart/self-care-tasks.desktop`; the application still runs as
the logged-in user, with access to the touchscreen, display, and network
settings. If the repository is moved, run the installer again.

To inspect why startup failed, run:

```sh
scripts/start.sh
```

To remove the startup entry:

```sh
sh scripts/install-autostart.sh --uninstall
```
