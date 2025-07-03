import sys
import os
import re
import threading
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QCheckBox, QProgressBar,
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QTabWidget, QTextEdit,
    QFrame, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread

from huggingface_hub import list_repo_files, hf_hub_download

import os
import sys
from PyQt5 import QtCore
from ui.splash import show_splash
from ui.main_window import HFDownloader

# 强制设置 Qt 插件路径（确保打包后也能找到）
# __file__ 会指向 onefile 临时目录或解压目录
base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
plugin_path = os.path.join(base_dir, "PyQt5", "Qt", "plugins", "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path


APP_VERSION = "v2.0"
APP_AUTHOR = "Accelemate"
APP_GITHUB = "https://github.com/Accelemate"
APP_CSDN = "https://blog.csdn.net/m0_60610428"
APP_JUEJIN = "https://juejin.cn/user/1479280118214153"

DEFAULT_PROXY = {
    "enabled": False,
    "protocol": "socks5",
    "host": "localhost",
    "port": 7890
}
DEFAULT_THEME = "light"

THEMES = {
    "light": """
        QWidget { background: #f7f7f7; color: #222; font-size: 20px;}
        QLineEdit, QComboBox, QSpinBox { background: #fff; border: 1.5px solid #bbb; border-radius: 8px; padding: 8px; font-size: 20px;}
        QPushButton { background: #4e8cff; color: #fff; border-radius: 8px; padding: 8px 24px; font-size: 20px;}
        QPushButton:disabled { background: #aaa; }
        QProgressBar { border: 1.5px solid #bbb; border-radius: 8px; text-align: center; font-size: 18px;}
        QProgressBar::chunk { background: #4e8cff; }
        QCheckBox { padding: 6px; font-size: 18px;}
        QDialog { background: #f7f7f7;}
        QTextEdit { background: #fff; border: 1.5px solid #bbb; border-radius: 8px; padding: 8px; font-size: 18px;}
        QLabel { font-size: 20px;}
    """,
    "dark": """
        QWidget { background: #232629; color: #eee; font-size: 20px;}
        QLineEdit, QComboBox, QSpinBox { background: #2d2f31; border: 1.5px solid #444; border-radius: 8px; color: #eee; padding: 8px; font-size: 20px;}
        QPushButton { background: #4e8cff; color: #fff; border-radius: 8px; padding: 8px 24px; font-size: 20px;}
        QPushButton:disabled { background: #555; }
        QProgressBar { border: 1.5px solid #444; border-radius: 8px; text-align: center; font-size: 18px;}
        QProgressBar::chunk { background: #4e8cff; }
        QCheckBox { padding: 6px; font-size: 18px;}
        QDialog { background: #232629;}
        QTextEdit { background: #2d2f31; border: 1.5px solid #444; border-radius: 8px; color: #eee; padding: 8px; font-size: 18px;}
        QLabel { font-size: 20px;}
    """
}

class DownloadSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

class SettingsDialog(QDialog):
    def __init__(self, parent, proxy_config, theme):
        super().__init__(parent)
        self.setWindowTitle("系统设置")
        self.setMinimumSize(400, 350)
        self.proxy_config = proxy_config.copy()
        self.theme = theme
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget(self)
        # 系统设置页
        settings_widget = QWidget()
        layout = QFormLayout()
        self.proxy_enable = QCheckBox("启用代理")
        self.proxy_enable.setChecked(self.proxy_config["enabled"])
        layout.addRow(self.proxy_enable)
        self.proxy_protocol = QComboBox()
        self.proxy_protocol.addItems(["socks5"])
        self.proxy_protocol.setCurrentText(self.proxy_config["protocol"])
        layout.addRow("代理协议", self.proxy_protocol)
        self.proxy_host = QLineEdit(self.proxy_config["host"])
        layout.addRow("代理服务器", self.proxy_host)
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(self.proxy_config["port"])
        layout.addRow("代理端口", self.proxy_port)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.theme)
        layout.addRow("应用主题", self.theme_combo)
        settings_widget.setLayout(layout)
        self.tabs.addTab(settings_widget, "系统设置")
        # 关于页
        about_widget = QWidget()
        about_layout = QVBoxLayout()
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml(
            f"<b>Huggingface 数据集下载器</b><br>"
            f"版本：{APP_VERSION}<br>"
            f"作者：{APP_AUTHOR}<br>"
            f"<br>"
            f"<b>联系地址：</b><br>"
            f"GitHub：<a href='{APP_GITHUB}'>{APP_GITHUB}</a><br>"
            f"CSDN：<a href='{APP_CSDN}'>{APP_CSDN}</a><br>"
            f"稀土掘金：<a href='{APP_JUEJIN}'>{APP_JUEJIN}</a><br>"
        )
        about_layout.addWidget(about_text)
        about_widget.setLayout(about_layout)
        self.tabs.addTab(about_widget, "关于")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def get_settings(self):
        return {
            "proxy": {
                "enabled": self.proxy_enable.isChecked(),
                "protocol": self.proxy_protocol.currentText(),
                "host": self.proxy_host.text().strip(),
                "port": self.proxy_port.value()
            },
            "theme": self.theme_combo.currentText()
        }

class NetworkCheckWorker(QObject):
    finished = pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
    def run(self):
        import requests
        try:
            resp = requests.get("https://huggingface.co", timeout=5)
            self.finished.emit(resp.status_code == 200)
        except Exception:
            self.finished.emit(False)

class HFDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.proxy_config = DEFAULT_PROXY.copy()
        self.theme = DEFAULT_THEME
        self.stop_event = threading.Event()
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle(f'Huggingface 数据集下载器 {APP_VERSION}')
        if getattr(sys, 'frozen', False):
            BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ICON_PATH = os.path.join(BASE_DIR, "huggingface_download.ico")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # 顶部标题
        title = QLabel("Huggingface 数据集下载器")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:36px;font-weight:bold;margin-top:24px;margin-bottom:8px;")
        line = QLabel()
        line.setFixedHeight(2)
        line.setStyleSheet("background:#4e8cff;margin-bottom:18px;")

        # 参数区
        param_layout = QFormLayout()
        param_layout.setLabelAlignment(Qt.AlignRight)
        param_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        param_layout.setHorizontalSpacing(24)
        param_layout.setVerticalSpacing(18)
        self.repo_id_label = QLabel('数据集ID（repo_id）:')
        self.repo_id_input = QLineEdit()
        self.repo_id_input.setPlaceholderText('如：FreedomIntelligence/huatuo_knowledge_graph_qa')
        self.repo_type_label = QLabel('类型（repo_type）:')
        self.repo_type_combo = QComboBox()
        self.repo_type_combo.addItems(['dataset', 'model'])
        self.token_label = QLabel('访问令牌（token）:')
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('如：hf_xxx，获取：https://huggingface.co/settings/tokens')
        self.local_dir_label = QLabel('保存路径:')
        self.local_dir_input = QLineEdit()
        self.local_dir_input.setReadOnly(True)
        self.local_dir_btn = QPushButton('选择文件夹')
        self.local_dir_btn.clicked.connect(self.select_dir)
        self.symlink_checkbox = QCheckBox('使用符号链接（local_dir_use_symlinks）')
        self.symlink_checkbox.setChecked(False)
        self.resume_checkbox = QCheckBox('断点续传（resume_download）')
        self.resume_checkbox.setChecked(True)
        h_dir = QHBoxLayout()
        h_dir.addWidget(self.local_dir_input)
        h_dir.addWidget(self.local_dir_btn)
        param_layout.addRow(self.repo_id_label, self.repo_id_input)
        param_layout.addRow(self.repo_type_label, self.repo_type_combo)
        param_layout.addRow(self.token_label, self.token_input)
        param_layout.addRow(self.local_dir_label, h_dir)
        param_layout.addRow("", self.symlink_checkbox)
        param_layout.addRow("", self.resume_checkbox)

        # 进度区
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.status_label = QLabel("等待下载")
        self.status_label.setStyleSheet("font-size:18px;color:#888;margin-top:8px;")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton('开始下载')
        self.download_btn.clicked.connect(self.download_dataset)
        self.stop_btn = QPushButton('停止')
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        self.settings_btn = QPushButton('系统设置')
        self.settings_btn.clicked.connect(self.open_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addStretch()

        # 总体布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(line)
        main_layout.addLayout(param_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(progress_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def apply_theme(self):
        self.setStyleSheet(THEMES[self.theme])
        self.set_button_effects()

    def select_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择保存路径')
        if dir_path:
            self.local_dir_input.setText(dir_path)

    def open_settings(self):
        dlg = SettingsDialog(self, self.proxy_config, self.theme)
        if dlg.exec_():
            settings = dlg.get_settings()
            self.proxy_config = settings["proxy"]
            self.theme = settings["theme"]
            self.apply_theme()

    def set_proxy_env(self):
        if self.proxy_config["enabled"]:
            proxy_url = f'{self.proxy_config["protocol"]}://{self.proxy_config["host"]}:{self.proxy_config["port"]}'
            os.environ["ALL_PROXY"] = proxy_url
            os.environ["all_proxy"] = proxy_url
            os.environ["HTTP_PROXY"] = proxy_url
            os.environ["http_proxy"] = proxy_url
            os.environ["HTTPS_PROXY"] = proxy_url
            os.environ["https_proxy"] = proxy_url
        else:
            for var in ["ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"]:
                os.environ.pop(var, None)

    def check_network(self):
        try:
            resp = requests.get("https://huggingface.co", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def download_dataset(self):
        repo_id = self.repo_id_input.text().strip()
        repo_type = self.repo_type_combo.currentText()
        token = self.token_input.text().strip()
        base_dir = self.local_dir_input.text().strip()
        use_symlinks = self.symlink_checkbox.isChecked()
        resume = self.resume_checkbox.isChecked()
        if not repo_id:
            QMessageBox.warning(self, '错误', '请填写数据集ID（repo_id）')
            return
        if not token or not re.match(r'^hf_\w+', token):
            QMessageBox.warning(self, '错误', '请填写有效的访问令牌（token），格式如：hf_xxx')
            return
        if not base_dir:
            QMessageBox.warning(self, '错误', '请选择保存路径')
            return
        self.set_proxy_env()
        # 禁用所有控件，显示检测中
        self.setEnabled(False)
        self.status_label.setText("正在检测网络，请稍候...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # 网络检测线程
        self.net_thread = QThread()
        self.net_worker = NetworkCheckWorker()
        self.net_worker.moveToThread(self.net_thread)
        self.net_thread.started.connect(self.net_worker.run)
        self.net_worker.finished.connect(self._on_network_checked)
        self.net_worker.finished.connect(self.net_thread.quit)
        self.net_worker.finished.connect(self.net_worker.deleteLater)
        self.net_thread.finished.connect(self.net_thread.deleteLater)
        self.net_thread.start()
        # 参数暂存
        self._download_params = dict(
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
            base_dir=base_dir,
            use_symlinks=use_symlinks,
            resume=resume
        )

    def _on_network_checked(self, ok):
        QApplication.restoreOverrideCursor()
        self.setEnabled(True)
        if not ok:
            self.status_label.setText("网络检测失败")
            QMessageBox.critical(self, '网络错误', '无法连接到 huggingface.co，请检查网络或开启VPN/代理。')
            return
        else:
            self.status_label.setText("网络连接正常，可以开始下载！")
            QMessageBox.information(self, '网络正常', '网络连接正常，可以开始下载！')
        # 进入实际下载
        self._start_download(**self._download_params)

    def _start_download(self, repo_id, repo_type, token, base_dir, use_symlinks, resume):
        folder_name = repo_id.split('/')[-1] if '/' in repo_id else repo_id
        save_path = os.path.join(base_dir, folder_name)
        os.makedirs(save_path, exist_ok=True)
        self.stop_event.clear()
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.settings_btn.setEnabled(False)
        self.status_label.setText("下载中...")
        self.progress_bar.setValue(0)
        QApplication.processEvents()
        self.signals = DownloadSignals()
        self.signals.progress.connect(self.progress_bar.setValue)
        self.signals.finished.connect(self.download_finished)
        def download_thread():
            try:
                files = list_repo_files(repo_id=repo_id, repo_type=repo_type, token=token)
                total = len(files)
                if total == 0:
                    self.signals.finished.emit(False, "数据集文件列表为空")
                    return
                for idx, file in enumerate(files):
                    if self.stop_event.is_set():
                        self.signals.finished.emit(False, "下载被用户终止")
                        return
                    hf_hub_download(
                        repo_id=repo_id,
                        repo_type=repo_type,
                        filename=file,
                        local_dir=save_path,
                        local_dir_use_symlinks=use_symlinks,
                        resume_download=resume,
                        token=token,
                        force_download=False
                    )
                    percent = int((idx + 1) / total * 100)
                    self.signals.progress.emit(percent)
                self.signals.finished.emit(True, save_path)
            except Exception as e:
                self.signals.finished.emit(False, str(e))
        threading.Thread(target=download_thread, daemon=True).start()

    def stop_download(self):
        self.stop_event.set()
        self.status_label.setText("下载已终止")
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.settings_btn.setEnabled(True)
        QMessageBox.information(self, "提示", "下载已被用户终止。")

    def download_finished(self, success, info):
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.settings_btn.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("下载完成")
            QMessageBox.information(self, '成功', f'下载完成！文件已保存至：\n{info}')
        else:
            self.progress_bar.setValue(0)
            self.status_label.setText("下载失败" if info != "下载被用户终止" else "下载已终止")
            if info != "下载被用户终止":
                QMessageBox.critical(self, '下载失败', f'下载失败：{info}')

    def set_button_effects(self):
        # 按钮点击效果：按下变深色，松开恢复
        def make_effect(btn, normal, pressed):
            btn.setStyleSheet(normal)
            btn.pressed.connect(lambda: btn.setStyleSheet(pressed))
            btn.released.connect(lambda: btn.setStyleSheet(normal))
        # 主题色
        if self.theme == 'dark':
            normal = "background:#4e8cff;color:#fff;border-radius:8px;padding:8px 24px;font-size:20px;"
            pressed = "background:#2560a8;color:#fff;border-radius:8px;padding:8px 24px;font-size:20px;"
        else:
            normal = "background:#4e8cff;color:#fff;border-radius:8px;padding:8px 24px;font-size:20px;"
            pressed = "background:#2560a8;color:#fff;border-radius:8px;padding:8px 24px;font-size:20px;"
        make_effect(self.download_btn, normal, pressed)
        make_effect(self.stop_btn, normal, pressed)
        make_effect(self.settings_btn, normal, pressed)
        make_effect(self.local_dir_btn, normal, pressed)

def main():
    app = QApplication(sys.argv)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "resources", "huggingface_download.ico")
    show_splash(app, ICON_PATH)
    win = HFDownloader()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()