import json

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QStackedWidget,
    QMessageBox,
)

from PySide6.QtCore import Qt, Signal
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"
DATA_FILE = BASE_DIR / "data.json"

class SettingsWindow(QMainWindow):

    exit_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoReplayBuffer")
        self.resize(600, 450)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        # =========================
        # Load Files
        # =========================

        self.config = self.load_config()
        self.data = self.load_data()

        # =========================
        # Menu Bar
        # =========================

        menu_bar = self.menuBar()

        obs_action = menu_bar.addAction("OBS")
        games_action = menu_bar.addAction("Games")
        exit_action = menu_bar.addAction("Exit")

        exit_action.triggered.connect(
            self.exit_requested.emit
        )
        
        obs_action.triggered.connect(self.show_obs)
        games_action.triggered.connect(self.show_games)

        # =========================
        # Pages
        # =========================

        self.pages = QStackedWidget()

        self.obs_page = self.create_obs_page()
        self.games_page = self.create_games_page()

        self.pages.addWidget(self.obs_page)
        self.pages.addWidget(self.games_page)

        self.main_layout.addWidget(self.pages)

        self.pages.setCurrentWidget(self.obs_page)


    # =========================================================
    # CLOSE EVENT
    # =========================================================

    def closeEvent(self, event):

        event.ignore()
        self.hide()

    # =========================================================
    # CONFIG.JSON
    # =========================================================
    def load_config(self):

        default_config = {
            "obs": {
                "host": "localhost",
                "port": 4455,
                "password": ""
            }
        }

        if not CONFIG_FILE.exists():

            self.save_config(default_config)

            return default_config

        try:

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                config = json.load(file)

        except (
            json.JSONDecodeError,
            OSError
        ):

            self.save_config(default_config)

            return default_config

        if "obs" not in config:

            config["obs"] = default_config["obs"]

            self.save_config(config)

        return config
    
    def save_config(self, config):

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                config,
                file,
                indent=4,
                ensure_ascii=False
            )

    # =========================================================
    # DATA.JSON
    # =========================================================

    def load_data(self):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            data = {}

            self.save_data(data)

            return data

    def save_data(self, data):

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    # =========================================================
    # OBS PAGE
    # =========================================================

    def create_obs_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)

        # =========================
        # Title
        # =========================

        title = QLabel("OBS WebSocket")

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(title)

        # =========================
        # IP
        # =========================

        ip_label = QLabel("IP Address")

        self.ip_entry = QLineEdit()

        self.ip_entry.setText(
            self.config["obs"]["host"]
        )

        layout.addWidget(ip_label)
        layout.addWidget(self.ip_entry)

        # =========================
        # Port
        # =========================

        port_label = QLabel("Port")

        self.port_entry = QLineEdit()

        self.port_entry.setText(
            str(self.config["obs"]["port"])
        )

        layout.addWidget(port_label)
        layout.addWidget(self.port_entry)

        # =========================
        # Password
        # =========================

        password_label = QLabel("Password")

        self.password_entry = QLineEdit()

        self.password_entry.setText(
            self.config["obs"]["password"]
        )

        self.password_entry.setPlaceholderText(
            "OBS WebSocket Password"
        )

        self.password_entry.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        layout.addWidget(password_label)
        layout.addWidget(self.password_entry)

        # =========================
        # Save
        # =========================

        self.obs_save_button = QPushButton(
            "Save"
        )

        self.obs_save_button.clicked.connect(
            self.save_obs
        )

        layout.addStretch()

        layout.addWidget(
            self.obs_save_button
        )

        return page

    # =========================================================
    # GAMES PAGE
    # =========================================================

    def create_games_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)

        # =========================
        # Title
        # =========================

        title = QLabel("Process Scanner")

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(title)

        # =========================
        # Description
        # =========================

        description = QLabel(
            "Add games or programs that should be scanned."
        )

        layout.addWidget(description)

        # =========================
        # Game List
        # =========================

        self.process_list = QListWidget()

        layout.addWidget(
            self.process_list
        )

        # Load games from data.json

        for game_name in self.data:

            self.process_list.addItem(
                game_name
            )

        # When selecting a game

        self.process_list.itemClicked.connect(
            self.select_game
        )

        # =========================
        # Game Name
        # =========================

        game_label = QLabel(
            "Game Name"
        )

        self.game_entry = QLineEdit()

        self.game_entry.setPlaceholderText(
            "e.g. Overwatch"
        )

        layout.addWidget(
            game_label
        )

        layout.addWidget(
            self.game_entry
        )

        # =========================
        # Process
        # =========================

        process_label = QLabel(
            "Process"
        )

        self.process_entry = QLineEdit()

        self.process_entry.setPlaceholderText(
            "e.g. overwatch or overwatch.exe"
        )

        layout.addWidget(
            process_label
        )

        layout.addWidget(
            self.process_entry
        )

        # =========================
        # Buttons
        # =========================

        button_layout = QHBoxLayout()

        # Add

        add_button = QPushButton(
            "Add Game"
        )

        add_button.clicked.connect(
            self.add_game
        )

        # Update

        update_button = QPushButton(
            "Update Game"
        )

        update_button.clicked.connect(
            self.update_game
        )

        button_layout.addWidget(
            add_button
        )

        button_layout.addWidget(
            update_button
        )

        layout.addLayout(
            button_layout
        )

        # =========================
        # Remove
        # =========================

        remove_button = QPushButton(
            "Remove Selected"
        )

        remove_button.clicked.connect(
            self.remove_game
        )

        layout.addWidget(
            remove_button
        )

        return page

    # =========================================================
    # SELECT GAME
    # =========================================================

    def select_game(self, item):

        game_name = item.text()

        if game_name not in self.data:
            return

        process = self.data[game_name].get(
            "process",
            ""
        )

        # Fill inputs

        self.game_entry.setText(
            game_name
        )

        self.process_entry.setText(
            process
        )

    # =========================================================
    # ADD GAME
    # =========================================================

    def add_game(self):

        game_name = (
            self.game_entry
            .text()
            .strip()
        )

        process = (
            self.process_entry
            .text()
            .strip()
        )

        # =========================
        # Validate Game Name
        # =========================

        if not game_name:

            QMessageBox.warning(
                self,
                "Error",
                "Please enter a game name."
            )

            return

        # =========================
        # Validate Process
        # =========================

        if not process:

            QMessageBox.warning(
                self,
                "Error",
                "Please enter a process name."
            )

            return

        # =========================
        # Add .exe
        # =========================

        if not process.lower().endswith(
            ".exe"
        ):

            process += ".exe"

        # =========================
        # Check Duplicate
        # =========================

        if game_name in self.data:

            QMessageBox.warning(
                self,
                "Already Exists",
                "This game already exists."
            )

            return

        # =========================
        # Save
        # =========================

        self.data[game_name] = {
            "process": process
        }

        self.save_data(
            self.data
        )

        # Add to List

        self.process_list.addItem(
            game_name
        )

        # Clear inputs

        self.game_entry.clear()
        self.process_entry.clear()

        QMessageBox.information(
            self,
            "Saved",
            f"{game_name} added successfully."
        )

    # =========================================================
    # UPDATE GAME
    # =========================================================

    def update_game(self):

        selected_item = (
            self.process_list.currentItem()
        )

        # =========================
        # Check Selection
        # =========================

        if selected_item is None:

            QMessageBox.warning(
                self,
                "Error",
                "Please select a game first."
            )

            return

        # =========================
        # Old Game Name
        # =========================

        old_game_name = selected_item.text()

        # =========================
        # New Values
        # =========================

        new_game_name = (
            self.game_entry
            .text()
            .strip()
        )

        process = (
            self.process_entry
            .text()
            .strip()
        )

        # =========================
        # Validate
        # =========================

        if not new_game_name:

            QMessageBox.warning(
                self,
                "Error",
                "Game name cannot be empty."
            )

            return

        if not process:

            QMessageBox.warning(
                self,
                "Error",
                "Process cannot be empty."
            )

            return

        # =========================
        # Add .exe
        # =========================

        if not process.lower().endswith(
            ".exe"
        ):

            process += ".exe"

        # =========================
        # Check Name Conflict
        # =========================

        if (
            new_game_name != old_game_name
            and new_game_name in self.data
        ):

            QMessageBox.warning(
                self,
                "Already Exists",
                "Another game already uses this name."
            )

            return

        # =========================
        # Update Data
        # =========================

        # Remove old entry

        del self.data[old_game_name]

        # Create new entry

        self.data[new_game_name] = {
            "process": process
        }

        # Save data.json

        self.save_data(
            self.data
        )

        # =========================
        # Update List
        # =========================

        selected_item.setText(
            new_game_name
        )

        # =========================
        # Update Input
        # =========================

        self.game_entry.setText(
            new_game_name
        )

        self.process_entry.setText(
            process
        )

        QMessageBox.information(
            self,
            "Updated",
            f"{new_game_name} updated successfully."
        )

    # =========================================================
    # REMOVE GAME
    # =========================================================

    def remove_game(self):

        selected_item = (
            self.process_list.currentItem()
        )

        if selected_item is None:

            QMessageBox.warning(
                self,
                "Error",
                "Please select a game first."
            )

            return

        game_name = selected_item.text()

        # =========================
        # Confirmation
        # =========================

        result = QMessageBox.question(
            self,
            "Remove Game",
            f"Are you sure you want to remove {game_name}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        # =========================
        # Remove from data
        # =========================

        if game_name in self.data:

            del self.data[game_name]

        self.save_data(
            self.data
        )

        # =========================
        # Remove from List
        # =========================

        row = self.process_list.row(
            selected_item
        )

        self.process_list.takeItem(
            row
        )

        # =========================
        # Clear Inputs
        # =========================

        self.game_entry.clear()
        self.process_entry.clear()

        QMessageBox.information(
            self,
            "Removed",
            f"{game_name} removed successfully."
        )

    # =========================================================
    # SAVE OBS
    # =========================================================

    def save_obs(self):

        host = (
            self.ip_entry
            .text()
            .strip()
        )

        port_text = (
            self.port_entry
            .text()
            .strip()
        )

        password = (
            self.password_entry
            .text()
        )

        # =========================
        # Validate Host
        # =========================

        if not host:

            QMessageBox.warning(
                self,
                "Error",
                "IP Address cannot be empty."
            )

            return

        # =========================
        # Validate Port
        # =========================

        try:

            port = int(port_text)

        except ValueError:

            QMessageBox.warning(
                self,
                "Error",
                "Port must be a number."
            )

            return

        if port < 1 or port > 65535:

            QMessageBox.warning(
                self,
                "Error",
                "Port must be between 1 and 65535."
            )

            return

        # =========================
        # Save OBS
        # =========================

        self.config["obs"] = {
            "host": host,
            "port": port,
            "password": password
        }

        self.save_config(
            self.config
        )

        QMessageBox.information(
            self,
            "Saved",
            "OBS settings saved successfully."
        )

    # =========================================================
    # PAGE NAVIGATION
    # =========================================================

    def show_obs(self):

        self.pages.setCurrentWidget(
            self.obs_page
        )

    def show_games(self):

        self.pages.setCurrentWidget(
            self.games_page
        )


