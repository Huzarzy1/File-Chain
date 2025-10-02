import sys
import os
import requests
from requests.auth import HTTPBasicAuth
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
QListWidget, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt

class FileTransferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileChain Client")
        self.setGeometry(100, 100, 600, 400)

        # Server configuration
        self.server_url = " "   # Replace with actual server IP and port
        self.auth = HTTPBasicAuth('username', 'password')  # Replace with actual credentials

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # GUI elements
        self.upload_btn = QPushButton("Select File(s) to Upload")
        self.upload_btn.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_btn)

        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        self.refresh_btn = QPushButton("Refresh File List")
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        self.layout.addWidget(self.refresh_btn)

        self.download_btn = QPushButton("Download Selected File")
        self.download_btn.clicked.connect(self.download_file)
        self.layout.addWidget(self.download_btn)

        self.delete_btn = QPushButton("Delete Selected File")
        self.delete_btn.clicked.connect(self.delete_file)
        self.layout.addWidget(self.delete_btn)


        # Initial file list population
        self.refresh_file_list()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    response = requests.post(f"{self.server_url}/upload", files=files, auth=self.auth)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", response.json()['message'])
                    self.refresh_file_list()
                else:
                    QMessageBox.critical(self, "Error", response.json()['error'])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")

    def refresh_file_list(self):
        try:
            response = requests.get(f"{self.server_url}/files", auth=self.auth)
            if response.status_code == 200:
                self.file_list.clear()
                for file in response.json()['files']:
                    self.file_list.addItem(file)
            else:
                QMessageBox.critical(self, "Error", response.json()['error'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch files: {str(e)}")

    def download_file(self):
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a file to download")
            return
        selected_file = selected_item.text()
        try:
            response = requests.get(f"{self.server_url}/download/{selected_file}", auth=self.auth)
            if response.status_code == 200:
                save_path, _ = QFileDialog.getSaveFileName(self, "Save File", selected_file)
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Success", f"File {selected_file} downloaded to {save_path}")
            else:
                QMessageBox.critical(self, "Error", response.json()['error'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")

    def delete_file(self):
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a file to delete")
            return
        selected_file = selected_item.text()
        try:
            response = requests.delete(f"{self.server_url}/delete/{selected_file}", auth=self.auth)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", f"{selected_file} deleted.")
                self.refresh_file_list()
            else:
                QMessageBox.critical(self, "Error", response.json()['error'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTransferApp()
    window.show()
    sys.exit(app.exec())