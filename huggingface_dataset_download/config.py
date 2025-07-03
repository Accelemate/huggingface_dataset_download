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