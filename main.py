import argparse
import PyQt5.QtGui
import minecraft_launcher_lib
import subprocess
import os
import shutil
import psutil
from datetime import datetime
import sys
import logging
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal
import requests
import json
import PyQt5.QtCore
from PyQt5.QtWidgets import QTextBrowser
import platform
from PyQt5 import QtWidgets, QtCore

# Обработка аргументов командной строки
parser = argparse.ArgumentParser()
parser.add_argument('--version', type=float, help='Specify the current version')
parser.add_argument('--newVersion', type=float, help='Specify the new version')
parser.add_argument('--UserStatusWeb', type=str, help='Specify the user status web resource')
parser.add_argument('--LoginUrl', type=str, help='Specify the login URL')
parser.add_argument('--bruh_debug', action='store_true', help='Enable debug mode')
parser.add_argument('--CustomDatabase', type=str, help='Specify the path to a custom JSON database file')
args = parser.parse_args()

with open("NotSetLog.log", "w+") as log:
    log.flush()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('NotSetLog.log', 'a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class RequestThread(QThread):
    finished = pyqtSignal(int, str)
    error = pyqtSignal(str)

    @staticmethod
    def auth_user(nickname, password, stage):
        url = "http://23.177.184.54:1234/json"
        data = {
            "stage": stage,
            "login": nickname,
            "pass": password
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "auth|reg failed"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    '''

    def __init__(self, nickname, password):
        super(RequestThread, self).__init__()
        self.nickname = nickname
        self.password = password
        
    def run(self):
        if args.bruh_debug and args.CustomDatabase:
            try:
                with open(args.CustomDatabase, 'r') as file:
                    data = json.load(file)
                    for user in data:
                        if user['nickname'] == self.nickname and user['password'] == self.password:
                            self.finished.emit(200, json.dumps(user))
                            logging.info(f"Login attempt with nickname: {self.nickname}, using custom database")
                            return
                    self.finished.emit(401, "Invalid credentials")
            except Exception as e:
                self.error.emit(str(e))
                logging.error(f"Error reading custom database: {str(e)}")
        else:
            try:
                url = args.LoginUrl if args.LoginUrl else 'https://raw.githubusercontent.com/SashegDev/test/main/database.json'
                data = {'nickname': self.nickname, 'password': self.password}
                response = requests.get(url, data=data)
                if response.status_code == 200:
                    user_data_list = json.loads(response.text)
                    for user_data in user_data_list:
                        if user_data['nickname'] == self.nickname and user_data['password'] == self.password:
                            self.finished.emit(200, json.dumps(user_data))
                            logging.info(f"Login attempt with nickname: {self.nickname}, status code: {response.status_code}")
                            return
                    self.finished.emit(401, "Invalid credentials")
                else:
                    self.finished.emit(response.status_code, response.text)
            except requests.exceptions.RequestException as e:
                self.error.emit(str(e))
                logging.error(f"Login error with nickname: {self.nickname}, error: {str(e)}")
    '''
    @staticmethod
    def fetch_user_status(nickname):
        if args.bruh_debug and args.CustomDatabase:
            try:
                with open(args.CustomDatabase, 'r') as file:
                    data = json.load(file)
                    for user in data:
                        if user['nickname'] == nickname:
                            return user['status'], user['role']
                    return None, None
            except Exception as e:
                logging.error(f"Failed to read custom database: {str(e)}")
                return None, None
        else:
            url = args.UserStatusWeb if args.UserStatusWeb else 'https://raw.githubusercontent.com/SashegDev/test/main/database.json'
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = json.loads(response.text)
                for user in data:
                    if user['nickname'] == nickname:
                        return user['status'], user['role']
                return None, None
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch user status: {str(e)}")
                return None, None

            

class QTextBrowserHandler(logging.Handler):
    def __init__(self, text_browser):
        super().__init__()
        self.text_browser = text_browser

    def emit(self, record):
        msg = self.format(record)
        self.text_browser.append(msg)
            

class Ui(QtWidgets.QMainWindow):
    def __init__(self, debug_mode):
        super(Ui, self).__init__()
        self.debug_mode = debug_mode

        self.version = 1.14
        self.creators = ['SashegDev', 'NoisySpektr(GDKipper)', 'BitGen Studios']
        self.timestamp = "01.09.2024"
        self.up_version = 1.2

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)

        self.setWindowTitle("BG Launcher - Login")
        self.login_ui_path = 'login.ui'
        self.launcher_ui_path = 'launcher.ui'
        uic.loadUi(self.login_ui_path, self)
        self.nickname_input = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.password_input = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.login_button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.login_button.clicked.connect(self.on_login_clicked)

        self.remember_password_checkbox = self.findChild(QtWidgets.QCheckBox, 'rememberPassword')
        self.stay_logged_checkbox = self.findChild(QtWidgets.QCheckBox, 'stayLogged')

        self.remember_password_checkbox.stateChanged.connect(self.on_checkbox_login)
        self.stay_logged_checkbox.stateChanged.connect(self.on_checkbox_login)

        self.register_button = self.findChild(QtWidgets.QPushButton, 'registerButton')
        self.register_button.clicked.connect(self.on_register_clicked)

        self.load_login_options()
        self.save_login_options()
        
        self.show()
        
        Ui.Update_Checker(self)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('NotSetLog.log', 'a')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self.auto_login()

    def on_checkbox_login(self):
        self.save_login_options()

    def load_login_options(self):
        try:
            with open('BGLauncherOptions_Login.json', 'r') as f:
                options = json.load(f)

            self.remember_password_checkbox.setChecked(options.get("rememberPassword", False))
            self.stay_logged_checkbox.setChecked(options.get("stayLogged", False))

            self.nickname_input.setText(options.get("lastNickname", ""))
            if self.remember_password_checkbox.isChecked():
                self.password_input.setText(options.get("lastPassword", ""))

            logging.info("Login options loaded successfully.")

        except FileNotFoundError:
            logging.warning("Options file not found. Using default settings.")
        except json.JSONDecodeError:
            logging.error("Error decoding options file. Using default settings.")

    def save_login_options(self):
        options = {
            "rememberPassword": self.remember_password_checkbox.isChecked(),
            "stayLogged": self.stay_logged_checkbox.isChecked(),
            "lastNickname": self.nickname_input.text(),
            "lastPassword": self.password_input.text() if self.remember_password_checkbox.isChecked() else ""
        }

        with open('BGLauncherOptions_Login.json', 'w') as f:
            json.dump(options, f, indent=4)

        logging.info("Login options saved successfully.")

    def auto_login(self):
        # Проверяем, что stayLogged отмечен и пароль не пустой
        if self.stay_logged_checkbox.isChecked() and self.password_input.text():
            self.on_login_clicked()


    def on_login_clicked(self):
        self.authenticate_user("pass")

    def on_register_clicked(self):
        stage = 'reg'
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        self.login_button.setEnabled(False)
        self.nickname_input.setEnabled(False)
        self.password_input.setEnabled(False)
        nickname = self.nickname_input.text()
        password = self.password_input.text()
        logging.info(f"{stage.capitalize()} button clicked with nickname: {nickname}")

        if self.debug_mode:
            logging.info("Debug mode enabled, skipping request")
            self.handle_response(200, "Debug mode")
        else:
            self.request_thread = RequestThread.auth_user(nickname, password, stage)
            self.request_thread.finished.connect(self.handle_response)
            self.request_thread.error.connect(self.show_error_message)
            self.request_thread.start()

    def authenticate_user(self):
        stage = 'pass'
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        self.login_button.setEnabled(False)
        self.nickname_input.setEnabled(False)
        self.password_input.setEnabled(False)
        nickname = self.nickname_input.text()
        password = self.password_input.text()
        logging.info(f"{stage.capitalize()} button clicked with nickname: {nickname}")

        if self.debug_mode:
            logging.info("Debug mode enabled, skipping request")
            self.handle_response(200, "Debug mode")
        else:
            self.request_thread = RequestThread.auth_user(nickname, password, stage)
            self.request_thread.finished.connect(self.handle_response)
            self.request_thread.error.connect(self.show_error_message)
            self.request_thread.start()

    def handle_response(self, status_code, response_text):
        self.enable_inputs()
        if status_code == 200:
            self.open_launcher_ui(self.nickname_input.text(), "User")
        elif status_code == 401:
            self.show_error_message("Invalid credentials")
        else:
            self.show_error_message(response_text)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._startPos = event.pos()

    def mouseMoveEvent(self, event):
        if self._startPos is not None:
            delta = event.pos() - self._startPos
            new_pos = self.pos() + delta

            # Получаем размер экрана
            screen_rect = QtWidgets.QApplication.desktop().availableGeometry(self)

            # Проверяем, чтобы новое положение окна не выходило за пределы экрана
            if new_pos.x() < screen_rect.left():
                new_pos.setX(screen_rect.left())
            if new_pos.y() < screen_rect.top():
                new_pos.setY(screen_rect.top())
            if new_pos.x() + self.width() > screen_rect.right():
                new_pos.setX(screen_rect.right() - self.width())
            if new_pos.y() + self.height() > screen_rect.bottom():
                new_pos.setY(screen_rect.bottom() - self.height())

            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._startPos = None


    def LoggerMessage(self):
        logging.getLogger().info("Hello! This is a\n========= BitGen Launcher! =========\n")
        logging.getLogger().info("This launcher has maded by:")
        for i in range(len(self.creators)):
            logging.getLogger().info("* "+self.creators[i])
        logging.getLogger().info("\n\n\nLauncher running on:")
        logging.getLogger().info(f"Launcher version: {self.version}")
        logging.getLogger().info(f"TimeStamp of verison: {self.timestamp}")
        logging.getLogger().info(f"UpdateCenter Version: {self.up_version}")
        logging.getLogger().info("SYSTEM TYPE: "+str(platform.system()))
        logging.getLogger().info("OS: "+str(platform.platform()))
        logging.getLogger().info("Total RAM: "+str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB")


    def UpdateMessage(self, curver, newver):
        self.enable_inputs()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("UPDATE FOUND")
        msg.setInformativeText(f"Update Found!\nCurrent version:{curver}\nNew Version:{newver}")
        msg.setWindowTitle("info")
        msg.exec_()

    def Message(self, title, text, mode):
        self.enable_inputs()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setWindowTitle(mode)
        msg.exec_()

    def Update_Checker(self):
        test_version = args.version if args.version else self.version
        new_version = args.newVersion if args.newVersion else None
        if new_version:
            if new_version > test_version:
                Ui.UpdateMessage(self, test_version, new_version)
                sys.exit(100)
        else:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            url = 'https://raw.githubusercontent.com/SashegDev/test/main/curver.txt'
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = float(response.text)
                if data > test_version:
                    Ui.UpdateMessage(self, test_version, data)
                    sys.exit(100)

                logger.setLevel(logging.NOTSET)
            except requests.exceptions.RequestException as e:
                logger.setLevel(logging.NOTSET)
                logging.error("Failed to fetch UpdateCenter")
                Ui.Message(self, "ERROR", "Failed to fetch UpdateCenter", "error")

    def on_login_clicked(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        self.login_button.setEnabled(False)
        self.nickname_input.setEnabled(False)
        self.password_input.setEnabled(False)
        nickname = self.nickname_input.text()
        password = self.password_input.text()
        logging.info(f"Login button clicked with nickname: {nickname}")
    
        if self.debug_mode:
            logging.info("Debug mode enabled, skipping login request")
            self.handle_response(200, "Debug mode")
        else:
            self.request_thread = RequestThread(nickname, password)
            self.request_thread.finished.connect(self.handle_response)
            self.request_thread.error.connect(self.show_error_message)
            self.request_thread.start()

#    def handle_response(self, status_code, response_text):
#        self.enable_inputs()
#        if status_code == 200:
#            nickname = self.nickname_input.text()
#            status, role = RequestThread.fetch_user_status(nickname)
#            if status == 'Active':
#                self.open_launcher_ui(nickname, role)
#            elif status == 'InActive':
#                self.show_inactive_message()
#            else:
#                self.show_error_message("User not found or invalid status")
#        elif status_code == 401:
#            self.show_error_message("Invalid credentials")
#        else:
#            self.show_error_message(response_text)
    

    def show_error_message(self, error_text):
        self.enable_inputs()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Login Error")
        msg.setInformativeText(f"An error occurred during login: {error_text}")
        msg.setWindowTitle("Error")
        msg.exec_()

    def show_inactive_message(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Account Inactive")
        msg.setInformativeText("This account is inactive and requires activation.")
        msg.setWindowTitle("Inactive Account")
        msg.exec_()
        self.close()
        self.__init__(self.debug_mode)

    def show_error_loading_message(self, error_text):
        self.enable_inputs()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(f"An error occurred: {error_text}")
        msg.setWindowTitle("Error")
        msg.exec_()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._startPos = event.pos()

    def enable_inputs(self):
        self.login_button.setEnabled(True)
        self.nickname_input.setEnabled(True)
        self.password_input.setEnabled(True)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._startPos = None

    def open_launcher_ui(self, nickname, role):
        self.close()
        self.launcher_ui = QtWidgets.QMainWindow()

        uic.loadUi(self.launcher_ui_path, self.launcher_ui)
        self.nickname_label = self.launcher_ui.findChild(QtWidgets.QLabel, 'nickname')
        if self.nickname_label is not None:
            self.nickname_label.setText(nickname)
        self.status_label = self.launcher_ui.findChild(QtWidgets.QLabel, 'userStatus')
        if self.status_label is not None:
            self.status_label.setText(role)
        self.play_button = self.launcher_ui.findChild(QtWidgets.QPushButton, 'PLAY')
        if self.play_button is not None:
            self.play_button.clicked.connect(self.on_play_clicked)

        self.comboBox = self.launcher_ui.findChild(QtWidgets.QComboBox, 'comboBox')

        self.InstalledVersionsCheckBox = self.launcher_ui.findChild(QtWidgets.QCheckBox, 'only_installed_versions')
        if self.InstalledVersionsCheckBox is not None:
            self.InstalledVersionsCheckBox.stateChanged.connect(self.on_checkbox_state_changed)

        if self.comboBox is not None:
            self.load_minecraft_versions()
            self.comboBox.currentIndexChanged.connect(self.on_version_selected)

        self.leaveaccount = self.launcher_ui.findChild(QtWidgets.QPushButton, 'leaveaccount')
        if self.leaveaccount is not None:
            self.leaveaccount.clicked.connect(self.AccountLeave)

        self.accountinfo = self.launcher_ui.findChild(QtWidgets.QPushButton, 'userinfo')
        if self.accountinfo is not None:
            self.accountinfo.clicked.connect(self.AccountInfo)

        self.ram_slider = self.launcher_ui.findChild(QtWidgets.QSlider, 'ram')
        self.width_input = self.launcher_ui.findChild(QtWidgets.QLineEdit, 'width')
        self.height_input = self.launcher_ui.findChild(QtWidgets.QLineEdit, 'height')

        self.saveoptions = self.launcher_ui.findChild(QtWidgets.QPushButton, 'saveoptions')
        if self.saveoptions is not None:
            self.saveoptions.clicked.connect(self.save_launcher_options)

        self.news = self.launcher_ui.findChild(QTextBrowser, 'news')
        self.news.textChanged.connect(self.amogus)

        self.regusers = self.launcher_ui.findChild(QTextBrowser, 'regusers')
        if self.regusers is not None:
            self.load_registered_users()

        logger = logging.getLogger()
        if not any(isinstance(h, QTextBrowserHandler) for h in logger.handlers):
            handler = QTextBrowserHandler(self.news)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        self.load_launcher_options()

        # Добавляем обработчики событий мыши для окна лаунчера
        self.launcher_ui.mousePressEvent = self.mousePressEvent
        self.launcher_ui.mouseMoveEvent = self.mouseMoveEvent
        self.launcher_ui.mouseReleaseEvent = self.mouseReleaseEvent

        self.launcher_ui.show()

        Ui.LoggerMessage(self)

    def amogus(self):
        scroll_bar = self.news.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def load_registered_users(self):
        try:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            url = args.LoginUrl if args.LoginUrl else 'https://raw.githubusercontent.com/SashegDev/test/main/database.json'
            response = requests.get(url)
            response.raise_for_status()

            data = json.loads(response.text)
            user_list = [f"* {user['nickname']} - {user['role']}" for user in data]

            self.regusers.setPlainText("\n".join(user_list))

            logger.setLevel(logging.NOTSET)

        except requests.exceptions.RequestException as e:
            logger.setLevel(logging.NOTSET)
            logging.error(f"Failed to fetch registered users: {str(e)}")
            self.regusers.setPlainText("Failed to load users.")

    def load_launcher_options(self):
        try:
            with open('BGLauncherOptions.json', 'r') as f:
                options = json.load(f)

            self.width_input.setText(options.get("resolutionWidth", "854"))
            self.height_input.setText(options.get("resolutionHeight", "480"))
            self.ram_slider.setValue(options.get("ram", 1024))

            version = options.get("selectedVersion", "")
            index = self.comboBox.findText(version)
            if index != -1:
                self.comboBox.setCurrentIndex(index)

            self.InstalledVersionsCheckBox.setChecked(options.get("showOnlyInstalled", False))

            logging.info("Launcher options loaded successfully.")

        except FileNotFoundError:
            logging.warning("Options file not found. Using default settings.")
        except json.JSONDecodeError:
            logging.error("Error decoding options file. Using default settings.")

    def save_launcher_options(self):
        options = {
            "resolutionWidth": self.width_input.text(),
            "resolutionHeight": self.height_input.text(),
            "ram": self.ram_slider.value(),
            "selectedVersion": self.comboBox.currentText(),
            "showOnlyInstalled": self.InstalledVersionsCheckBox.isChecked()
        }

        with open('BGLauncherOptions.json', 'w') as f:
            json.dump(options, f, indent=4)

        logging.info("Launcher options saved successfully.")


#    def SaveOptions(self):
#        # Создание словаря с настройками
#        options = {
#            "resolutionWidth": self.width_input.text(),
#            "resolutionHeight": self.height_input.text(),
#            "ram": self.ram_slider.value(),
#            "selectedVersion": self.comboBox.currentText(),
#            "showOnlyInstalled": self.InstalledVersionsCheckBox.isChecked(),
#            "rememberPassword": self.remember_password_checkbox.isChecked(),
#            "stayLogged": self.stay_logged_checkbox.isChecked(),
#            "lastNickname": self.nickname_input.text(),
#            "lastPassword": self.password_input.text() if self.remember_password_checkbox.isChecked() else ""
#        }
#
#        # Сохранение настроек в файл
#        with open('BGLauncherOptions.json', 'w') as f:
#            json.dump(options, f, indent=4)
#
#        logging.info("Options saved successfully.")

    def AccountLeave(self):
        # Закрываем текущее окно
        self.launcher_ui.close()

        # Открываем окно входа
        self.__init__(self.debug_mode)
        self.show()

    def AccountInfo(self):
        try:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            url = args.LoginUrl if args.LoginUrl else 'https://raw.githubusercontent.com/SashegDev/test/main/database.json'
            response = requests.get(url)
            response.raise_for_status()

            logger.setLevel(logging.NOTSET)

            data = json.loads(response.text)
            nickname = self.nickname_label.text()

            user_info = next((user for user in data if user['nickname'] == nickname), None)

            if user_info:
                status = user_info.get('status', 'Unknown')
                role = user_info.get('role', 'Unknown')
                message = f"Nickname: {nickname}\nStatus: {status}\nRole: {role}"
            else:
                message = "User not found."

            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Account Information")
            msg.setInformativeText(message)
            msg.setWindowTitle("Account Info")
            msg.exec_()

        except requests.exceptions.RequestException as e:
            logger.setLevel(logging.NOTSET)
            logging.error(f"Failed to fetch account info: {str(e)}")
            self.show_error_loading_message("Failed to fetch account info.")

    def on_checkbox_state_changed(self):
        state = self.InstalledVersionsCheckBox.isChecked()
        self.load_minecraft_versions(state)

    def load_minecraft_versions(self, show_only_installed=False):
        self.comboBox.clear()
        versions = []

        fabric_versions = minecraft_launcher_lib.fabric.get_stable_minecraft_versions()
        forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
        vanilla_versions = minecraft_launcher_lib.utils.get_version_list()

        if show_only_installed:
            installed_versions = minecraft_launcher_lib.utils.get_installed_versions("bglauncher")
            installed_ids = {version['id'] for version in installed_versions}

            versions.extend(f"Fabric {version}" for version in fabric_versions if version in installed_ids)
            versions.extend(f"Forge {version}" for version in forge_versions if version in installed_ids)
            versions.extend(f"Vanilla {version['id']}" for version in vanilla_versions if version["type"] == "release" and version['id'] in installed_ids)

        else:
            versions.extend(f"Fabric {version}" for version in fabric_versions)
            versions.extend(f"Forge {version}" for version in forge_versions)
            versions.extend(f"Vanilla {version['id']}" for version in vanilla_versions if version["type"] == "release")
            
        if len(versions) > 1:
            self.comboBox.setEnabled(True)
            self.comboBox.addItems(versions)
        else:
            self.comboBox.addItem("NO VERSIONS FOUND")
            self.comboBox.setEnabled(False)




    def on_version_selected(self, index):
        selected_version = self.comboBox.itemText(index)
        if selected_version != "NO VERSIONS FOUND":
            logging.info(f"Selected version: {selected_version}")
        else:
            logging.info("PLEASE INSTALL ATLEAST 1 VERSION FOR PLAY")

    def on_play_clicked(self):
        selected_version = self.comboBox.currentText()
        version_type, version_id = selected_version.split(' ', 1)

        mc_options = {
            "launcherName": 'BitGen Launcher',
            "launcherVersion": str(self.version),
            'username': self.nickname_label.text(),
            'uuid': '',
            'token': '',
            "customResolution": True,
            "resolutionWidth": self.width_input.text(),
            "resolutionHeight": self.height_input.text(),
            "jvmArguments": [f"-Xms{self.ram_slider.value()}M", f"-Xmx{self.ram_slider.value()}M"]
        }

        installed_versions = minecraft_launcher_lib.utils.get_installed_versions("bglauncher")
        version_installed = any(version['id'] == version_id for version in installed_versions)

        if not version_installed:
            self.install_thread = InstallThread(version_type, version_id, "bglauncher")
            self.install_thread.finished.connect(lambda: self.launch_minecraft(version_id, mc_options))
            self.install_thread.error.connect(self.show_error_loading_message)
            self.install_thread.start()
        else:
            self.launch_minecraft(version_id, mc_options)

    def launch_minecraft(self, version_id, mc_options):
        try:
            subprocess.call(minecraft_launcher_lib.command.get_minecraft_command(version_id, "bglauncher", mc_options))
        except Exception as e:
            logging.error(f"Error during launch: {str(e)}")
            self.show_error_loading_message(str(e))

    def run():
        logging.getLogger().debug(msg="\n\n"+"=-"*5+" LAUNCHING MC "+"=-"*5)

    @staticmethod
    def copy_log_file():
        project_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(project_dir, 'logs')

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file_name = f'{current_date}.log'
        log_file_path = os.path.join(logs_dir, log_file_name)

        if os.path.exists(log_file_path):
            counter = 1
            while True:
                new_log_file_name = f'{current_date}_{counter}.log'
                new_log_file_path = os.path.join(logs_dir, new_log_file_name)
                if not os.path.exists(new_log_file_path):
                    log_file_path = new_log_file_path
                    break
                counter += 1

        shutil.copy('NotSetLog.log', log_file_path)
        logging.info(f"Log file copied to {log_file_path}")

class InstallThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, version_type, version_id, minecraft_directory):
        super(InstallThread, self).__init__()
        self.version_type = version_type
        self.version_id = version_id
        self.minecraft_directory = minecraft_directory

    def run(self):
        try:
            if self.version_type == "Fabric":
                minecraft_launcher_lib.fabric.install_fabric(self.version_id, self.minecraft_directory)
            elif self.version_type == "Forge":
                minecraft_launcher_lib.forge.install_forge_version(self.version_id, self.minecraft_directory)
            elif self.version_type == "Vanilla":
                minecraft_launcher_lib.install.install_minecraft_version(self.version_id, self.minecraft_directory)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


if __name__ == "__main__":
    debug_mode = args.bruh_debug
    if debug_mode:
        logging.info("Debug mode enabled")

    try:
        app = QtWidgets.QApplication(sys.argv)
        window = Ui(debug_mode)
        app.exec_()
        Ui.copy_log_file()
    except Exception as e:
        logging.exception("Unhandled exception occurred")
        raise
