from PyQt5.QtWidgets import QDialog, QTabWidget, QWidget, QFormLayout, QCheckBox, QComboBox, QLineEdit, QSpinBox, QTextEdit, QVBoxLayout, QDialogButtonBox
from config import APP_VERSION, APP_AUTHOR, APP_GITHUB, APP_CSDN, APP_JUEJIN

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