from PyQt5.QtCore import QObject, pyqtSignal
import requests

class NetworkCheckWorker(QObject):
    finished = pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
    def run(self):
        try:
            resp = requests.get("https://huggingface.co", timeout=5)
            self.finished.emit(resp.status_code == 200)
        except Exception:
            self.finished.emit(False) 