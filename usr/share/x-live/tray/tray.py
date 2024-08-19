#!/usr/bin/python3

import sys
import xupdates
import subprocess
import os
import urllib.request
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox, QLabel
from PyQt5.QtGui import QIcon

# Pfad zum gewünschten Arbeitsverzeichnis # Das Arbeitsverzeichnis festlegen
arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/tray')

os.chdir(arbeitsverzeichnis)

class SystemTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.update = {}


        # Create the icon
        self.tray_icon = QSystemTrayIcon(QIcon("./x-live-tray.png"), self.app)
        self.tray_icon.setToolTip("X-Live Tools")

        # mögliche befehle
        self.settings_cmds =  self.check_cmds(["x-mint-settings","xfce4-settings-manager","lxde-control-center","gnome-control-center","systemsettings"]).split("\n")
        self.term_cmds = self.check_cmds(["gnome-terminal","konsole","xfce4-terminal","lxterminal"]).split("\n")
        self.taskm_cmds = self.check_cmds(["gnome-system-monitor","ksysguard","xfce4-taskmanager","lxtask","stacer"]).split("\n")
        self.update_cmds = self.check_cmds(["x-live-update","update-manager","mintupdate","muon-updater","discover","gnome-software","aptitude"]).split("\n")

        # Befehlsdefinition
        self.tmcommand = self.taskm_cmds[0]
        self.termcommand = self.term_cmds[0]
        self.settingscommand = self.settings_cmds[0]
        self.updatecommand = self.update_cmds[0]

        # Create the menu
        self.menu = QMenu("tool")

        self.l1_action = QAction("System Apps")
        self.menu.addAction(self.l1_action)
        #self.l2_action = QAction("")
        #self.menu.addAction(self.l2_action)

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

        
        if self.check_cmd("ufw")!="":
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

        if self.check_cmd("x-live-hardwareinfo")!="":
            self.hwi_action = QAction("Hardwareinformationen")
            self.hwi_action.triggered.connect(lambda: subprocess.Popen("x-live-hardwareinfo"))
            self.hwi_action.setIcon(QIcon('./icons/hardware'))
            self.menu.addAction(self.hwi_action)

        if self.check_cmd("x-live-driver")!="":
            self.nvidia_action = QAction("↳ NVidia Treiber")
            self.nvidia_action.triggered.connect(lambda: subprocess.Popen("x-live-driver"))
            self.nvidia_action.setIcon(QIcon.fromTheme('x-live-driver'))
            self.menu.addAction(self.nvidia_action)

        if self.check_cmd("x-live-webai")!="":
            self.webai_action = QAction("WebAI Chatbot")
            self.webai_action.triggered.connect(lambda: subprocess.Popen("x-live-webai"))
            self.webai_action.setIcon(QIcon('/usr/share/pixmaps/webai'))
            self.menu.addAction(self.webai_action)

        
        if self.check_cmd("x-live-cp")!="":
            self.fullc_action = QAction("ControlPanel")
            self.fullc_action.triggered.connect(lambda: subprocess.Popen("x-live-cp"))
            self.fullc_action.setIcon(QIcon('/usr/share/pixmaps/x-live-cp'))
            self.menu.addAction(self.fullc_action)
            self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.update_check()


        self.autostart_action = QAction("□\tAutostart")
        if os.path.exists(os.path.expanduser("~/.config/autostart/x-live-tray.desktop")):
            self.autostart_action.setText("✓\tAutostart")
        self.autostart_action.triggered.connect(self.toogle_autostart)
        self.menu.addAction(self.autostart_action)


        self.exit_action = QAction("Beenden")
        self.exit_action.triggered.connect(self.exit_app)
        self.exit_action.setIcon(QIcon.fromTheme('application-exit'))
        self.menu.addAction(self.exit_action)
        

        # Set up the tray icon
        self.tray_icon.setContextMenu(self.menu)
        #self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
      
    def com(self, command):
        try:
            # Führe den übergebenen Befehl aus und erfasse die Ausgabe
            result = subprocess.check_output(command, shell=True).decode("UTF-8")
            #print(f"befehl:{command}\tErgebnis:{result}")
            return result
        except subprocess.CalledProcessError as e:
            #print(f"Befehl: {str(command)}\tFehler: {e} \n")
            return " "

    def check_cmds(self, cmds):
        ergebnis = ""
        for cmd in cmds:
            
            t=self.com("command -v "+cmd)
            if t != " ":
                ergebnis = ergebnis + t
        return ergebnis
  
    def check_cmd(self, cmd):
        ergebnis = ""
        command = "command -v "+str(cmd)
        ergebnis = self.com(command).replace(" ","").replace("\n","")
        return ergebnis
   
    def toogle_autostart(self):
        PATH = os.path.expanduser("~/.config/autostart/x-live-tray.desktop")
        if os.path.exists(PATH):
            os.system("rm "+PATH)
        else:
            os.system("cp /usr/share/x-live/tray/x-live-tray.desktop "+PATH)

        if os.path.exists(PATH):
            self.autostart_action.setText("✓\tAutostart")
        else:
            self.autostart_action.setText("□\tAutostart")

    def show_message(self):
        QMessageBox.information(None, "Info", "This is a message from the system tray!")

    def exit_app(self):
        self.tray_icon.hide()
        sys.exit()

    def run(self):
        sys.exit(self.app.exec_())

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            subprocess.Popen("x-live-cp")

    def update_check(self):
        author = "verendert"
        repos = ["x-live-cp","x-live-tray","x-mint-settings","x-live-hardwareinfo", "x-live-easyeggs", "x-live-radio", "x-live-webai"]
        update_list = []

        try:
            url = "https://raw.githubusercontent.com/VerEnderT/x-live-tray/main/x-live-apps"
            with urllib.request.urlopen(url) as file:
                # Datei zeilenweise lesen
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

        if update_list != []:
            #pkgshort = package.split("-")[2]
            mehrzahl=""
            if len(update_list)>=2: mehrzahl="s"
            self.x_live_update = QAction(f"{len(update_list)} Update{mehrzahl} verfügbar !")
            self.x_live_update.setIcon(QIcon('./icons/update'))
            list_tt = "\n".join(update_list)
            print(f"updates: {list_tt}")
            #self.x_live_update.setToolTip("updates: {list_tt}")
            self.x_live_update.setStatusTip(f"Updates verfügbar für: {list_tt}")
            self.x_live_update.triggered.connect(lambda: subprocess.Popen("x-live-apps-update"))

            self.menu.addAction(self.x_live_update)

if __name__ == "__main__":
    app = SystemTrayApp()
    app.run()
