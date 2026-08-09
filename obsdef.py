import os
import time
import subprocess
from pathlib import Path
import psutil
import obsws_python as obs

from scanner import is_process_running


clinte = None
obs_started_by_script = False
replay_buffer_running = False


# =========================================================
#                     CONNECT TO OBS
# =========================================================

def connect_obs():
    for attempt in range(10):
        try:
            print(f"Connecting to OBS... ({attempt + 1}/10)")

            return obs.ReqClient(
                host="localhost",
                port=4455,
                password="123123"
            )

        except Exception as e:
            print(f"OBS not ready: {e}")
            time.sleep(1)

    print("Could not connect to OBS.")
    return None


# =========================================================
#                        RUN OBS
# =========================================================

def run_obs():
    global clinte
    global obs_started_by_script
    global replay_buffer_running

    if replay_buffer_running:
        return True

    if not is_process_running("obs64.exe"):
        obs_path = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
        obs_folder = r"C:\Program Files\obs-studio\bin\64bit"

        subprocess.Popen(
            [obs_path, "--minimize-to-tray"],
            cwd=obs_folder
        )

        obs_started_by_script = True

    clinte = connect_obs()

    if clinte is None:
        return False

    try:
        clinte.start_replay_buffer()
        replay_buffer_running = True

        print("Replay Buffer started.")

        return True

    except Exception as e:
        print(f"Failed to start Replay Buffer: {e}")
        return False


# =========================================================
#                       CLOSE OBS
# =========================================================

def close_obs():
    global obs_started_by_script
    if obs_started_by_script:
        for process in psutil.process_iter(["name"]):
            process_name = process.info["name"]

            if process_name and process_name.lower() == "obs64.exe":
                process.kill()
                print("OBS process killed")
                return

        print("OBS process not found")


# =========================================================
#                    CLEAN SHUTDOWN
# =========================================================

def clean_shutdown():
    sentinel_dir = (
        Path(os.getenv("APPDATA"))
        / "obs-studio"
        / ".sentinel"
    )

    if sentinel_dir.exists():
        for file in sentinel_dir.glob("run_*"):
            file.unlink()


# =========================================================
#              STOP REPLAY BUFFER + OBS
# =========================================================

def stop_rec_obs_if_by_script():
    global clinte
    global obs_started_by_script
    global replay_buffer_running

    if clinte and replay_buffer_running:
        try:
            clinte.stop_replay_buffer()

        except Exception as e:
            print(f"Failed to stop Replay Buffer: {e}")

        replay_buffer_running = False

    time.sleep(2)

    if obs_started_by_script:
        close_obs()
        obs_started_by_script = False

