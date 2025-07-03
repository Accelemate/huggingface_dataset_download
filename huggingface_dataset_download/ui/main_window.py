import os
import re
import threading
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QCheckBox, QProgressBar, QFormLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread
from config import DEFAULT_PROXY, DEFAULT_THEME, THEMES
from ui.settings_dialog import SettingsDialog
from core.network import NetworkCheckWorker
from core.downloader import Downloader

class HFDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.proxy_config = DEFAULT_PROXY.copy()
        self.theme = DEFAULT_THEME
        self.stop_event = threading.Event()
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle('Huggingface 数据集下载器')
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ICON_PATH = os.path.join(BASE_DIR, "..", "resources", "huggingface_download.ico")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        title = QLabel("Huggingface 数据集下载器")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:36px;font-weight:bold;margin-top:24px;margin-bottom:8px;")
        line = QLabel()
        line.setFixedHeight(2)
        line.setStyleSheet("background:#4e8cff;margin-bottom:18px;")
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
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.status_label = QLabel("等待下载")
        self.status_label.setStyleSheet("font-size:18px;color:#888;margin-top:8px;")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
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
        self.setEnabled(False)
        self.status_label.setText("正在检测网络，请稍候...")
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
        self._download_params = dict(
            repo_id=repo_id,
            repo_type=repo_type,
            token=token,
            base_dir=base_dir,
            use_symlinks=use_symlinks,
            resume=resume
        )

    def _on_network_checked(self, ok):
        self.setEnabled(True)
        if not ok:
            self.status_label.setText("网络检测失败")
            QMessageBox.critical(self, '网络错误', '无法连接到 huggingface.co，请检查网络或开启VPN/代理。')
            return
        else:
            self.status_label.setText("网络连接正常，可以开始下载！")
            QMessageBox.information(self, '网络正常', '网络连接正常，可以开始下载！')
        self._start_download(**self._download_params)

    def _start_download(self, repo_id, repo_type, token, base_dir, use_symlinks, resume):
        self.stop_event.clear()
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.settings_btn.setEnabled(False)
        self.status_label.setText("下载中...")
        self.progress_bar.setValue(0)
        self.downloader = Downloader(self.stop_event)
        self.downloader.signals.progress.connect(self.progress_bar.setValue)
        self.downloader.signals.finished.connect(self.download_finished)
        self.downloader.start_download(repo_id, repo_type, token, base_dir, use_symlinks, resume)

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
        def make_effect(btn, normal, pressed):
            btn.setStyleSheet(normal)
            btn.pressed.connect(lambda: btn.setStyleSheet(pressed))
            btn.released.connect(lambda: btn.setStyleSheet(normal))
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