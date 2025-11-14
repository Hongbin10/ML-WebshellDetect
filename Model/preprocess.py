from PyQt5.QtCore import QObject, pyqtSignal
import os
import shutil
import hashlib
import subprocess


class DataProcessor(QObject):
    progress = pyqtSignal(str)  # 进度信号
    finished = pyqtSignal(str)  # 完成信号，返回输出目录
    error = pyqtSignal(str)  # 错误信号

    def __init__(self):
        super().__init__()
        self._stop = False
        self._is_running = False

    def stop(self):
        """停止处理"""
        if self._is_running:
            self._stop = True
            self.progress.emit("正在停止处理...")

    def is_running(self):
        return self._is_running

    def _get_valid_php_files(self, directory):
        """获取有效的PHP文件列表"""
        php_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.php'):
                    file_path = os.path.join(root, file)
                    php_files.append(file_path)
        return php_files

    def _check_php_syntax(self, file_path):
        """使用php -l检查PHP语法"""
        try:
            # 使用php -l检查语法
            cmd = ['php', '-l', file_path]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            
            # 如果输出包含"No syntax errors"，说明语法正确
            return b'No syntax errors' in output
            
        except subprocess.CalledProcessError:
            # 语法错误
            return False
        except Exception:
            # 其他错误
            return False

    def _process_file(self, file_path, output_dir):
        """处理单个文件"""
        try:
            # 计算MD5哈希
            with open(file_path, 'rb') as f:
                fdata = f.read()
            fmd5 = hashlib.md5(fdata).hexdigest()
            new_filename = fmd5 + '.php'
            new_filepath = os.path.join(output_dir, new_filename)

            # 复制文件
            shutil.copy2(file_path, new_filepath)

            # 验证复制结果
            if not os.path.exists(new_filepath) or os.path.getsize(new_filepath) == 0:
                if os.path.exists(new_filepath):
                    os.remove(new_filepath)
                return False
            return True
        except:
            return False

    def process_datasets(self, malicious_dir, benign_dir, output_base_dir):
        """处理恶意和正常样本数据集"""
        if self._is_running:
            self.error.emit("已有处理任务正在运行")
            return

        self._is_running = True
        self._stop = False

        try:
            # 直接使用传入的output_base_dir作为输出目录
            malicious_output = os.path.join(output_base_dir, "malicious")
            benign_output = os.path.join(output_base_dir, "benign")

            os.makedirs(malicious_output, exist_ok=True)
            os.makedirs(benign_output, exist_ok=True)

            self.progress.emit(f"输出目录: {output_base_dir}")

            # 处理恶意样本
            self.progress.emit("开始处理恶意样本...")
            self._process_dataset(malicious_dir, malicious_output, "恶意样本")

            # 处理正常样本
            if not self._stop:
                self.progress.emit("开始处理正常样本...")
                self._process_dataset(benign_dir, benign_output, "正常样本")

            if self._stop:
                self.progress.emit("处理已停止")
                shutil.rmtree(output_base_dir, ignore_errors=True)
            else:
                self.progress.emit("数据处理完成!")
                self.finished.emit(output_base_dir)

        except Exception as e:
            self.error.emit(f"处理出错: {str(e)}")
        finally:
            self._is_running = False

    def _process_dataset(self, input_dir, output_dir, dataset_name):
        """处理单个数据集"""
        php_files = self._get_valid_php_files(input_dir)
        total_files = len(php_files)
        processed = 0
        success = 0

        self.progress.emit(f"发现 {total_files} 个PHP文件需要处理")

        for file_path in php_files:
            if self._stop:
                return

            processed += 1
            progress = int((processed / total_files) * 100)

            # 检查语法
            if not self._check_php_syntax(file_path):
                self.progress.emit(f"[{progress}%] 语法错误: {os.path.basename(file_path)}")
                continue

            # 处理文件
            if self._process_file(file_path, output_dir):
                success += 1
                self.progress.emit(f"[{progress}%] 已处理: {os.path.basename(file_path)}")
            else:
                self.progress.emit(f"[{progress}%] 处理失败: {os.path.basename(file_path)}")

        self.progress.emit(f"{dataset_name}处理完成: 成功 {success}/{total_files} 文件")