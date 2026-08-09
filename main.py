import threading
import time
import pystray
from PIL import Image

from scanner import game_scan
from obsdef import (
    run_obs,
    stop_rec_obs_if_by_script,
    clean_shutdown,
    close_obs
)


def monitor():
    while True:
        try:
            scan = game_scan()

            if scan:
                run_obs()
            else:
                stop_rec_obs_if_by_script()
                clean_shutdown()
                close_obs()

            time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


def quit_app(icon, item):
    clean_shutdown()
    stop_rec_obs_if_by_script()
    icon.stop()


def main():
    image = Image.open("icon.ico")

    icon = pystray.Icon(
        "AutoReplayBuffer",
        image,
        "AutoReplayBuffer",
        menu=pystray.Menu(
            pystray.MenuItem("Exit", quit_app)
        )
    )

    threading.Thread(
        target=monitor,
        daemon=True
    ).start()

    icon.run()


if __name__ == "__main__":
    main()