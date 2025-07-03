from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from config import APP_VERSION, APP_AUTHOR
import time

def show_splash(app, icon_path):
    splash_pix = QPixmap(icon_path)
    splash = QDialog()
    splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.setFixedSize(500, 400)
    label = QLabel(splash)
    label.setPixmap(splash_pix.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    label.setAlignment(Qt.AlignCenter)
    label.setGeometry(180, 90, 140, 140)
    text = QLabel(f"<span style='font-size:32px;'>HDT下载器 {APP_VERSION}</span><br><span style='font-size:22px;'>作者：{APP_AUTHOR}</span>", splash)
    text.setAlignment(Qt.AlignCenter)
    text.setGeometry(0, 260, 500, 60)
    text.setStyleSheet("color:#4e8cff;")
    splash.show()
    app.processEvents()
    time.sleep(2)
    splash.close() 