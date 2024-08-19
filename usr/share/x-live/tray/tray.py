#!/usr/bin/python3

import sys
import xupdates
import subprocess
import os
import urllib.request
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/tray')
os.chdir(arbeitsverzeichnis)

class SystemTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Create the icon
        self.tray_icon = QSystemTrayIcon(QIcon("./x-live-tray.png"), self.app)
        self.tray_icon.setToolTip("X-Live Tools")

        # Menüerstellung und weitere Initialisierungen
        self.create_menu()

        # Start the timer to check for updates every hour
        self.update_check_timer = QTimer()
        self.update_check_timer.timeout.connect(self.update_check)
        self.update_check_timer.start(3600000)  # 3600000 ms = 1 hour

        # Initialer Aufruf der Update-Überprüfung
        self.update_check()

        # Anzeige des Tray-Icons
        self.tray_icon.show()

    def create_menu(self):
        # Menu und Aktionen erstellen
        self.menu = QMenu("tool")

        self.l1_action = QAction("System Apps")
        self.menu.addAction(self.l1_action)

        self.settings_action = QAction("Einstellungen")
        self.settings_action.triggered.connect(lambda: subprocess.Popen(self.settingscommand))
        self.settings_action.setIcon(QIcon("./icons/settings.png"))
        self.menu.addAction(self.settings_action)

        self.tm_action = QAction("Taskmanager")
        self.tm_action.triggered.connect(lambda: subprocess.Popen(self.tmcommand))
        self.tm_action.setIcon(QIcon("./icons/taskmanager.png"))
        self.menu.addAction(self.tm_action)

        self.term_action = QAction("Terminal")
        self.term_action.triggered.connect(lambda: subprocess.Popen(self.termcommand))
        self.term_action.setIcon(QIcon("./icons/terminal.png"))
        self.menu.addAction(self.term_action)

        if self.check_cmd("ufw") != "":
            self.ufw_action = QAction("Firewall")
            self.ufw_action.triggered.connect(lambda: subprocess.Popen("gufw"))
            self.ufw_action.setIcon(QIcon("./icons/firewall.png"))
            self.menu.addAction(self.ufw_action)

        self.update_action = QAction("System aktualisieren")
        self.update_action.triggered.connect(lambda: subprocess.Popen(self.updatecommand))
        self.update_action.setIcon(QIcon("./icons/update.png"))
        self.menu.addAction(self.update_action)

        self.menu.addSeparator()

        self.l3_action = QAction("X-Live Apps")
        self.menu.addAction(self.l3_action)

        if self.check_cmd("x-live-hardwareinfo") != "":
            self.hwi_action = QAction("Hardwareinformationen")
            self.hwi_action.triggered.connect(lambda: subprocess.Popen("x-live-hardwareinfo"))
            self.hwi_action.setIcon(QIcon('./icons/hardware'))
            self.menu.addAction(self.hwi_action)

        if self.check_cmd("x-live-driver") != "":
            self.nvidia_action = QAction("↳ NVidia Treiber")
            self.nvidia_action.triggered.connect(lambda: subprocess.Popen("x-live-driver"))
            self.nvidia_action.setIcon(QIcon.fromTheme('x-live-driver'))
            self.menu.addAction(self.nvidia_action)

        if self.check_cmd("x-live-webai") != "":
            self.webai_action = QAction("WebAI Chatbot")
            self.webai_action.triggered.connect(lambda: subprocess.Popen("x-live-webai"))
            self.webai_action.setIcon(QIcon('/usr/share/pixmaps/webai'))
            self.menu.addAction(self.webai_action)

        if self.check_cmd("x-live-cp") != "":
            self.fullc_action = QAction("ControlPanel")
            self.fullc_action.triggered.connect(lambda: subprocess.Popen("x-live-cp"))
            self.fullc_action.setIcon(QIcon('/usr/share/pixmaps/x-live-cp'))
            self.menu.addAction(self.fullc_action)
            self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.autostart_action = QAction("□\tAutostart")
        if os.path.exists(os.path.expanduser("~/.config/autostart/x-live-tray.desktop")):
            self.autostart_action.setText("✓\tAutostart")
        self.autostart_action.triggered.connect(self.toogle_autostart)
        self.menu.addAction(self.autostart_action)

        self.exit_action = QAction("Beenden")
        self.exit_action.triggered.connect(self.exit_app)
        self.exit_action.setIcon(QIcon.fromTheme('application-exit'))
        self.menu.addAction(self.exit_action)

        self.tray_icon.setContextMenu(self.menu)

    def run(self):
        sys.exit(self.app.exec_())

    def com(self, command):
        try:
            result = subprocess.check_output(command, shell=True).decode("UTF-8")
            return result
        except subprocess.CalledProcessError as e:
            return " "

    def check_cmds(self, cmds):
        ergebnis = ""
        for cmd in cmds:
            t = self.com("command -v " + cmd)
            if t != " ":
                ergebnis = ergebnis + t
        return ergebnis

    def check_cmd(self, cmd):
        ergebnis = ""
        command = "command -v " + str(cmd)
        ergebnis = self.com(command).replace(" ", "").replace("\n", "")
        return ergebnis

    def toogle_autostart(self):
        PATH = os.path.expanduser("~/.config/autostart/x-live-tray.desktop")
        if os.path.exists(PATH):
            os.system("rm " + PATH)
        else:
            os.system("cp /usr/share/x-live/tray/x-live-tray.desktop " + PATH)

        if os.path.exists(PATH):
            self.autostart_action.setText("✓\tAutostart")
        else:
            self.autostart_action.setText("□\tAutostart")

    def exit_app(self):
        self.tray_icon.hide()
        sys.exit()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            subprocess.Popen("x-live-cp")

    def update_check(self):
        author = "verendert"
        repos = ["x-live-cp", "x-live-tray", "x-mint-settings", "x-live-hardwareinfo", "x-live-easyeggs", "x-live-radio", "x-live-webai"]
        update_list = []

        try:
            url = "https://raw.githubusercontent.com/VerEnderT/x-live-tray/main/x-live-apps"
            with urllib.request.urlopen(url) as file:
                lines = file.read().decode('utf-8').splitlines()

            if lines:
                repo = lines
                print(repo)
        except Exception as e:
            fehler = str(e).split(":")[-1]
            print(f"Fehler: {fehler}")

        for package in repos:
            try:
                test = xupdates.update_info(author, package)
                if test["update"] == "u":
                    print(f"\nNeue Version für {package} \nAktuell installiert: {test['installed']}\nVerfügbar: {test['version']}\nDownload-Url: {test['url']}")
                    update_list.append(package)
                if test['update'] == "a":
                    print(f"\n{package} ist installiert und aktuell! Version {test['installed']}")
            except Exception as e:
                fehler = str(e).split(":")[-1]
                print(f"Fehler: {fehler}")

        if hasattr(self, 'x_live_update') and self.x_live_update:
            self.menu.removeAction(self.x_live_update)

        if update_list:
            mehrzahl = "s" if len(update_list) >= 2 else ""
            self.x_live_update = QAction(f"{len(update_list)} Update{mehrzahl} verfügbar!")
            self.x_live_update.setIcon(QIcon('./icons/update.png'))
            list_tt = "\n".join(update_list)
            self.x_live_update.setStatusTip(f"Updates verfügbar für: {list_tt}")

            # Verbindung trennen, wenn Aktion ausgelöst wurde
            def handle_update_trigger():
                subprocess.Popen("x-live-apps-update")
                self.menu.removeAction(self.x_live_update)
                self.x_live_update = None

            self.x_live_update.triggered.connect(handle_update_trigger)
            self.menu.addAction(self.x_live_update)
        else:
            self.x_live_update = None

if __name__ == "__main__":
    app = SystemTrayApp()
    app.run()

