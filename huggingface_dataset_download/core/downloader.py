import threading
from PyQt5.QtCore import QObject, pyqtSignal
from huggingface_hub import list_repo_files, hf_hub_download
import os

class DownloadSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

class Downloader:
    def __init__(self, stop_event):
        self.signals = DownloadSignals()
        self.stop_event = stop_event

    def start_download(self, repo_id, repo_type, token, base_dir, use_symlinks, resume):
        folder_name = repo_id.split('/')[-1] if '/' in repo_id else repo_id
        save_path = os.path.join(base_dir, folder_name)
        os.makedirs(save_path, exist_ok=True)
        self.signals.progress.emit(0)
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