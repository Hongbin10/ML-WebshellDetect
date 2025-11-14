from PyQt5.QtCore import QThread, pyqtSignal
import os
import datetime
from Model.preprocess import DataProcessor

class PreprocessingThread(QThread):
    """数据预处理线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)  # 传递输出目录
    error = pyqtSignal(str)

    def __init__(self, malicious_dir, benign_dir, output_dir):
        super().__init__()
        self.malicious_dir = malicious_dir
        self.benign_dir = benign_dir
        self.output_dir = output_dir
        self.processor = DataProcessor()
        self.processor.progress.connect(self.progress.emit)
        self.processor.finished.connect(self.finished.emit)
        self.processor.error.connect(self.error.emit)

    def run(self):
        """运行数据处理线程"""
        try:
            # 创建时间戳目录
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamp_dir = os.path.join(self.output_dir, f"processed_data_{timestamp}")
            os.makedirs(timestamp_dir, exist_ok=True)
            
            # 创建子目录
            os.makedirs(os.path.join(timestamp_dir, "malicious"), exist_ok=True)
            os.makedirs(os.path.join(timestamp_dir, "benign"), exist_ok=True)

            
            # 处理数据集
            self.processor.process_datasets(
                self.malicious_dir,
                self.benign_dir,
                timestamp_dir
            )
            
        except Exception as e:
            self.error.emit(f"处理出错: {str(e)}")

    def stop(self):
        """停止处理"""
        self.processor.stop()