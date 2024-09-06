#!/usr/bin/python3

import sys
import os
import re
import subprocess
import xupdates
import urllib.request
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTextEdit
from PyQt5.QtCore import QProcess, QTimer
from PyQt5.QtGui import QTextCursor, QIcon


class GDebiClone(QMainWindow):
    def __init__(self, deb_file=None):
        super().__init__()

        self.setWindowTitle("X-Live Apps Updater ")
        self.setGeometry(100, 100, 400, 500)
        self.setMinimumWidth(450)
        icon = QIcon("/usr/share/x-live/apps-update/updates.png")
        self.setWindowIcon(icon)
        self.flag = True


        self.layout = QVBoxLayout()

        # Label to display selected file
        #self.label = QLabel("Verfügbare updates: ", self)
        #self.layout.addWidget(self.label)


        # Label to display package information
        self.info_label = QLabel("Keine Updates vorhanden", self)
        self.layout.addWidget(self.info_label)

        # Button to install the package
        self.install_button = QPushButton("Install Package", self)
        self.install_button.clicked.connect(self.start_install_packages)
        self.install_button.setEnabled(False)
        self.layout.addWidget(self.install_button)


        # Text area to show process output
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)
        self.output_area.hide()
        
        # Central widget
        central_widget = QWidget(self)
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        
        self.background_color()
        self.adjustSize()
        self.show
        self.url_list,self.update_list = self.update_check()

        self.deb_file = None
        self.process = None  # QProcess instance
        
    def start_install_packages(self):
        self.install_button.setEnabled(False)
        self.start_download(self.url_list)

    def install_packages(self):
        self.output_area.append("\nStarte Paket Installation...\n")
        self.output_area.moveCursor(QTextCursor.End)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.read_output)
        self.process.finished.connect(self.process_finished)
        
        # Prepare the command
        command = f'apt update && apt install -y /tmp/x-live/debs/*.deb'
        self.process.start('pkexec', ['sh', '-c', command])

    def read_output(self):
        if self.process:
            output = self.process.readAll().data().decode()
            output = output.replace('\r\n', '\n').replace('\r', '\n')
            self.output_area.moveCursor(QTextCursor.End)
            self.output_area.insertPlainText(output)
            self.output_area.moveCursor(QTextCursor.End)

    def process_finished(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.output_area.append("\nInstallation erfolgreich beendet!")
            self.output_area.moveCursor(QTextCursor.End)
            QMessageBox.information(self, "Erfolg", "Installation erfolgreich beendet!")
        else:
            self.output_area.append("\nInstallation fehlgeschlagen.")
            self.output_area.moveCursor(QTextCursor.End)
            QMessageBox.critical(self, "Fehler", "Installation Fehlgeschlagen.")
            
    # Farbprofil abrufen und anwenden

    def get_current_theme(self):
        try:
            # Versuche, das Theme mit xfconf-query abzurufen
            result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'], capture_output=True, text=True)
            theme_name = result.stdout.strip()
            if theme_name:
                return theme_name
        except FileNotFoundError:
            print("xfconf-query nicht gefunden. Versuche gsettings.")
        except Exception as e:
            print(f"Error getting theme with xfconf-query: {e}")

        try:
            # Fallback auf gsettings, falls xfconf-query nicht vorhanden ist
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
            theme_name = result.stdout.strip().strip("'")
            if theme_name:
                return theme_name
        except Exception as e:
            print(f"Error getting theme with gsettings: {e}")

        return None

    def extract_color_from_css(self,css_file_path, color_name):
        try:
            with open(css_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                #print(content)
                # Muster zum Finden der Farbe
                pattern = r'{}[\s:]+([#\w]+)'.format(re.escape(color_name))
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
                return None
        except IOError as e:
            print(f"Error reading file: {e}")
            return None
            
            
    def background_color(self):
        theme_name = self.get_current_theme()
        if theme_name:
            print(f"Current theme: {theme_name}")

            # Pfad zur GTK-CSS-Datei des aktuellen Themes
            css_file_path = f'/usr/share/themes/{theme_name}/gtk-3.0/gtk.css'
            if os.path.exists(css_file_path):
                bcolor = self.extract_color_from_css(css_file_path, ' background-color')
                color = self.extract_color_from_css(css_file_path, ' color')
                self.setStyleSheet(f"background: {bcolor};color: {color}")
            else:
                print(f"CSS file not found: {css_file_path}")
        else:
            print("Unable to determine the current theme.")

    def update_check(self):
        author = "verendert"
        repos = ["x-live-cp","x-live-tray","x-mint-settings","x-live-hardwareinfo", "x-live-easyeggs", "x-live-radio", "x-live-webai"]
        update_list = []
        aktuell_text_list = ""
        update_text_list = ""
        url_list = {}

        try:
            url = "https://raw.githubusercontent.com/VerEnderT/x-live-tray/main/x-live-apps"
            with urllib.request.urlopen(url) as file:
                # Datei zeilenweise lesen
                lines = file.read().decode('utf-8').splitlines()

            if lines:
                repos = lines
                print(repos)
        except Exception as e:
            fehler = str(e).split(":")[-1]
            print(f"Fehler: {fehler}")

        for package in repos:
            try:
                test = xupdates.update_info(author, package)
                if test["update"] == "u":
                    #print(f"\nNeue Version für {package} \nAktuell installiert: {test['installed']}\nVerfügbar: {test['version']}\nDownload-Url: {test['url']}")
                    update_text_list = update_text_list + (f"\n{package} \tinstalliert: {test['installed']}\tVerfügbar: {test['version']}")
                    update_list.append(package)
                    url_list[package]=test['url']
                    #print(test)

                if test['update'] == "a":
                    aktuell_text_list = aktuell_text_list + (f"\n{package} ist installiert und aktuell! Version {test['installed']}")
            except Exception as e:
                fehler = str(e).split(":")[-1]
                print(f"Fehler: {fehler}")

        if update_list != []:
            print(update_list)
            self.install_button.setEnabled(True)
            self.info_label.setText(f"aktuelle Apps:{aktuell_text_list}\n\nApps die aktuallsiert werden müssen:{update_text_list}")
        else:            
            self.info_label.setText(f"aktuelle Apps:{aktuell_text_list}\n\nApps die aktuallsiert werden müssen:\nkeine Updates verfügbar")
        return url_list,update_list

    # downloader

    def start_download(self, packages):
        self.output_area.show()
        self.adjustSize()
        if packages:
            self.packages = packages
            self.download_next_package()
        else:
            self.output_area.append("No packages to download.")

    def download_next_package(self):
        if self.packages:
            self.current_package, url = self.packages.popitem()
            package_filename = f"{self.current_package}.deb"
            self.output_area.append(f"Start downloading: {package_filename}")
            save_directory = '/tmp/x-live/debs/'

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            self.filename = os.path.join(save_directory, package_filename)

            if not self.process:
                self.process = QProcess(self)

            # Setup QProcess for wget command
            self.process.setProgram('wget')
            self.process.setArguments(['--progress=bar:force', '-O', self.filename, url])
            self.process.setWorkingDirectory(save_directory)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.handle_finished)
            self.process.start()
        else:
            if self.flag:            
                self.flag = False                
                self.output_area.append("All downloads finished.")
                QTimer.singleShot(1000, self.install_packages) 

    def handle_finished(self):
        self.output_area.append(f"Finished downloading: {self.filename}")
        QTimer.singleShot(1000, self.download_next_package)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    deb_file = sys.argv[1] if len(sys.argv) > 1 else None
    gdebi_clone = GDebiClone(deb_file=deb_file)
    gdebi_clone.show()
    sys.exit(app.exec_())




