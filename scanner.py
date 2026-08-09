import psutil
import json

with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


def is_process_running(process_name):
    for process in psutil.process_iter(["name"]):
        if process.info["name"] and process.info["name"].lower() == process_name.lower():
            return True

    return False


def game_scan():
    for game_name, game_info in data.items():
        if is_process_running(game_info["process"]):
            return game_name

    return None