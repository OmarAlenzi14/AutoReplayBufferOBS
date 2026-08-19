import sys
import json
import psutil
from pathlib import Path


# =========================================================
#                     DATA FILE PATH
# =========================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent


DATA_FILE = BASE_DIR / "data.json"


# =========================================================
#                      LOAD DATA
# =========================================================

def load_data():

    try:

        if not DATA_FILE.exists():

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {},
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return {}

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return {}


# =========================================================
#                CHECK PROCESS RUNNING
# =========================================================

def is_process_running(process_name):

    if not process_name:
        return False

    process_name = process_name.lower()

    for process in psutil.process_iter(["name"]):

        try:

            name = process.info["name"]

            if name and name.lower() == process_name:
                return True

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            continue

    return False


# =========================================================
#                      GAME SCAN
# =========================================================

def game_scan():

    data = load_data()

    for game_name, game_info in data.items():

        if not isinstance(game_info, dict):
            continue

        process_name = game_info.get("process")

        if not process_name:
            continue

        # Make sure process ends with .exe
        if not process_name.lower().endswith(".exe"):
            process_name += ".exe"

        if is_process_running(process_name):

            return game_name

    return None