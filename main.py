import sys
from pathlib import Path
import threading
import time

import pystray
from PIL import Image

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from widget import SettingsWindow

from scanner import game_scan

from obsdef import (
    run_obs,
    stop_rec_obs_if_by_script,
    clean_shutdown,
    close_obs
)


# =========================================================
#                     APPLICATION PATH
# =========================================================

if getattr(sys, "frozen", False):

    BASE_DIR = Path(sys.executable).resolve().parent

else:

    BASE_DIR = Path(__file__).resolve().parent


ICON_FILE = BASE_DIR / "icon.ico"


# =========================================================
#                     GLOBAL VARIABLES
# =========================================================

monitor_running = True
window = None
tray_icon = None
app = None


# =========================================================
#                     QT SIGNALS
# =========================================================

class AppSignals(QObject):

    show_settings = Signal()
    quit_app = Signal()


signals = AppSignals()


# =========================================================
#                       MONITOR
# =========================================================

def monitor():

    global monitor_running

    print("Monitor started.")

    while monitor_running:

        try:

            scan = game_scan()

            if scan:

                print(f"Game detected: {scan}")

                run_obs()

            else:

                stop_rec_obs_if_by_script()
                clean_shutdown()
                close_obs()

            time.sleep(5)

        except Exception as e:

            print(f"Monitor Error: {e}")

            time.sleep(5)

    print("Monitor stopped.")


# =========================================================
#                    SHOW SETTINGS
# =========================================================

def show_settings():

    global window

    if window is None:
        return

    window.show()
    window.raise_()
    window.activateWindow()


# =========================================================
#                     QUIT APP
# =========================================================

def quit_app():

    global monitor_running
    global window
    global tray_icon
    global app

    print("Shutting down AutoReplayBuffer...")

    # -----------------------------------------------------
    # Stop monitor
    # -----------------------------------------------------

    monitor_running = False

    # -----------------------------------------------------
    # Stop Replay Buffer
    # -----------------------------------------------------

    try:

        stop_rec_obs_if_by_script()

    except Exception as e:

        print(
            f"Failed to stop Replay Buffer: {e}"
        )

    # -----------------------------------------------------
    # Clean OBS
    # -----------------------------------------------------

    try:

        clean_shutdown()

    except Exception as e:

        print(
            f"Clean shutdown error: {e}"
        )

    # -----------------------------------------------------
    # Close OBS
    # -----------------------------------------------------

    try:

        close_obs()

    except Exception as e:

        print(
            f"OBS close error: {e}"
        )

    # -----------------------------------------------------
    # Close Settings Window
    # -----------------------------------------------------

    if window is not None:

        window.close()

    # -----------------------------------------------------
    # Stop Tray
    # -----------------------------------------------------

    if tray_icon is not None:

        try:

            tray_icon.stop()

        except Exception as e:

            print(
                f"Tray stop error: {e}"
            )

    # -----------------------------------------------------
    # Quit Qt
    # -----------------------------------------------------

    if app is not None:

        app.quit()


# =========================================================
#                     TRAY CALLBACKS
# =========================================================

def tray_show_settings(icon, item):

    signals.show_settings.emit()


def tray_exit(icon, item):

    signals.quit_app.emit()


# =========================================================
#                    START TRAY
# =========================================================

def start_tray():

    global tray_icon

    try:

        print("Starting tray...")

        # -------------------------------------------------
        # Check icon
        # -------------------------------------------------

        if not ICON_FILE.exists():

            raise FileNotFoundError(
                f"Icon not found: {ICON_FILE}"
            )

        # -------------------------------------------------
        # Load icon
        # -------------------------------------------------

        image = Image.open(ICON_FILE)

        # -------------------------------------------------
        # Tray menu
        # -------------------------------------------------

        menu = pystray.Menu(

            pystray.MenuItem(
                "Settings",
                tray_show_settings
            ),

            pystray.MenuItem(
                "Exit",
                tray_exit
            )

        )

        # -------------------------------------------------
        # Create tray
        # -------------------------------------------------

        tray_icon = pystray.Icon(
            "AutoReplayBuffer",
            image,
            "AutoReplayBuffer",
            menu
        )

        print("Tray created.")

        # -------------------------------------------------
        # Run tray
        # -------------------------------------------------

        tray_icon.run()

        print("Tray stopped.")

    except Exception as e:

        print(
            f"Tray Error: {e}"
        )

        signals.quit_app.emit()


# =========================================================
#                         MAIN
# =========================================================

def main():

    global window
    global app

    # =====================================================
    # Qt Application
    # =====================================================

    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    # =====================================================
    # Settings Window
    # =====================================================

    window = SettingsWindow()

    # =====================================================
    # Connect Signals
    # =====================================================

    signals.show_settings.connect(
        show_settings
    )

    signals.quit_app.connect(
        quit_app
    )

    # =====================================================
    # Widget → Exit
    # =====================================================

    window.exit_requested.connect(
        quit_app
    )

    # =====================================================
    # Start Monitor
    # =====================================================

    monitor_thread = threading.Thread(
        target=monitor,
        daemon=True
    )

    monitor_thread.start()

    # =====================================================
    # Start Tray
    # =====================================================

    tray_thread = threading.Thread(
        target=start_tray,
        daemon=True
    )

    tray_thread.start()

    # =====================================================
    # Start Qt
    # =====================================================

    print("AutoReplayBuffer started.")

    sys.exit(
        app.exec()
    )


# =========================================================
#                       ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()