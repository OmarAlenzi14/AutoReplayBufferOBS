import os
import sys
import time
import subprocess
import json
from pathlib import Path

import psutil
import obsws_python as obs

from scanner import is_process_running


# =========================================================
#                     BASE DIRECTORY
# =========================================================

if getattr(sys, "frozen", False):

    BASE_DIR = Path(
        sys.executable
    ).resolve().parent

else:

    BASE_DIR = Path(
        __file__
    ).resolve().parent


CONFIG_FILE = BASE_DIR / "config.json"


# =========================================================
#                     GLOBAL VARIABLES
# =========================================================

client = None

obs_started_by_script = False
replay_buffer_running = False


# =========================================================
#                     LOAD CONFIG
# =========================================================

def load_obs_config():

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(file)

        return config.get(
            "obs",
            {}
        )

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        print(
            f"Could not load config: {CONFIG_FILE}"
        )

        return {}


# =========================================================
#                     CONNECT TO OBS
# =========================================================

def connect_obs():

    obs_config = load_obs_config()

    host = obs_config.get(
        "host",
        "localhost"
    )

    port = obs_config.get(
        "port",
        4455
    )

    password = obs_config.get(
        "password",
        ""
    )

    for attempt in range(10):

        try:

            print(
                f"Connecting to OBS... "
                f"({attempt + 1}/10)"
            )

            return obs.ReqClient(
                host=host,
                port=port,
                password=password
            )

        except Exception as e:

            print(
                f"OBS not ready: {e}"
            )

            time.sleep(1)

    print(
        "Could not connect to OBS."
    )

    return None


# =========================================================
#                        RUN OBS
# =========================================================

def run_obs():

    global client
    global obs_started_by_script
    global replay_buffer_running

    # Already running

    if replay_buffer_running:

        return True

    # =====================================================
    # Start OBS if not running
    # =====================================================

    if not is_process_running(
        "obs64.exe"
    ):

        obs_path = (
            r"C:\Program Files\obs-studio"
            r"\bin\64bit\obs64.exe"
        )

        obs_folder = (
            r"C:\Program Files\obs-studio"
            r"\bin\64bit"
        )

        try:

            subprocess.Popen(
                [
                    obs_path,
                    "--minimize-to-tray"
                ],
                cwd=obs_folder
            )

            obs_started_by_script = True

            print(
                "OBS started by script."
            )

        except Exception as e:

            print(
                f"Failed to start OBS: {e}"
            )

            return False

    # =====================================================
    # Connect to OBS
    # =====================================================

    client = connect_obs()

    if client is None:

        return False

    # =====================================================
    # Start Replay Buffer
    # =====================================================

    try:

        client.start_replay_buffer()

        replay_buffer_running = True

        print(
            "Replay Buffer started."
        )

        return True

    except Exception as e:

        print(
            f"Failed to start Replay Buffer: {e}"
        )

        return False


# =========================================================
#                       CLOSE OBS
# =========================================================

def close_obs():

    global obs_started_by_script

    if not obs_started_by_script:

        return

    for process in psutil.process_iter(
        ["name"]
    ):

        try:

            process_name = process.info["name"]

            if (
                process_name
                and process_name.lower()
                == "obs64.exe"
            ):

                process.kill()

                print(
                    "OBS process killed."
                )

                return

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):

            continue

    print(
        "OBS process not found."
    )


# =========================================================
#                    CLEAN SHUTDOWN
# =========================================================

def clean_shutdown():

    appdata = os.getenv(
        "APPDATA"
    )

    if not appdata:

        return

    sentinel_dir = (
        Path(appdata)
        / "obs-studio"
        / ".sentinel"
    )

    if not sentinel_dir.exists():

        return

    for file in sentinel_dir.glob(
        "run_*"
    ):

        try:

            file.unlink()

            print(
                f"Removed sentinel: {file.name}"
            )

        except Exception as e:

            print(
                f"Failed to remove "
                f"{file.name}: {e}"
            )


# =========================================================
#              STOP REPLAY BUFFER + OBS
# =========================================================

def stop_rec_obs_if_by_script():

    global client
    global obs_started_by_script
    global replay_buffer_running

    # =====================================================
    # Stop Replay Buffer
    # =====================================================

    if (
        client
        and replay_buffer_running
    ):

        try:

            client.stop_replay_buffer()

            print(
                "Replay Buffer stopped."
            )

        except Exception as e:

            print(
                f"Failed to stop "
                f"Replay Buffer: {e}"
            )

        replay_buffer_running = False

    # =====================================================
    # Give OBS time
    # =====================================================

    time.sleep(2)

    # =====================================================
    # Close OBS only if script started it
    # =====================================================

    if obs_started_by_script:

        close_obs()

        obs_started_by_script = False

    # =====================================================
    # Clear client
    # =====================================================

    client = None