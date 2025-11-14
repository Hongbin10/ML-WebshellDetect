from PyQt5.QtCore import QThread, pyqtSignal
import pickle
from Model.train import (
    get_feature_for_train, train_model,
    get_file_opcode
)
from Model.database import Database
from datetime import datetime
import hashlib
import re
import os

class TrainingThread(QThread):
    """训练线程类"""
    progress = pyqtSignal(str)  # 进度信号
    finished = pyqtSignal(bool, dict)  # 完成信号，返回训练结果和评估指标
    error = pyqtSignal(str)  # 错误信号
    stopped = pyqtSignal()  # 停止信号
    progress_percent = pyqtSignal(int)  # 进度百分比信号

    def __init__(self, malicious_dir, benign_dir, model_type, user_id, dataset_id):
        super().__init__()
        self.malicious_dir = malicious_dir
        self.benign_dir = benign_dir
        self.model_type = model_type
        self.user_id = user_id
        self.dataset_id = dataset_id  # 保存数据集ID
        self.log_messages = []  # 存储日志消息
        self._stop_flag = False
        self._current_progress = 0
        self._total_files = 0
        self._processed_files = 0
        self._evaluation_metrics = ""  # 存储评估指标
        self.db = Database()  # 初始化数据库连接
        self.dataset_info = None  # 存储数据集信息
        self.is_running = True
        self.start_time = None  # 添加开始时间属性

    def format_duration(self, seconds):
        """将秒数转换为'X小时 X分钟 X秒'格式"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒"

    def stop(self):
        """停止训练"""
        self._stop_flag = True
        self.progress.emit('[INFO] 正在安全停止训练...')
        # 计算训练时长
        end_time = datetime.now()
        training_time = int((end_time - self.start_time).total_seconds() / 60)
        # 更新数据库中的状态
        self.db.save_training_log(
            user_id=self.user_id,
            model_name=self.model_type,
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            status="训练中断",
            start_time=self.start_time if self.start_time else datetime.now(),
            end_time=end_time,
            training_time=training_time,
            normal_dir=self.benign_dir,
            malicious_dir=self.malicious_dir
        )
        self.is_running = False

        
    def extract_features_async(self, input_dir, output_file, is_malicious=True):
        """异步提取特征"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            def is_md5_filename(filename):
                return re.fullmatch(r"[a-fA-F0-9]{32}\.php", filename) is not None

            invalid_files = [f for f in os.listdir(input_dir)
                             if f.endswith('.php') and not is_md5_filename(f)]

            if invalid_files:
                raise Exception(
                    f"检测到未预处理文件，请先运行数据预处理模块。"
                    f"不合法文件示例：{invalid_files[:3]}"
                )
            # 获取文件列表
            files = [f for f in os.listdir(input_dir) if f.endswith('.php')]
            total_files = len(files)
            if total_files == 0:
                raise Exception(f"目录 {input_dir} 中没有找到PHP文件")
                
            # 更新总文件数
            self._total_files += total_files
            start_progress = self._current_progress
            progress_range = 40 if is_malicious else 40  # 恶意和正常样本各占40%的进度
            
            # 分批处理文件
            batch_size = 10  # 每批处理10个文件
            processed_files = []
            
            for i in range(0, total_files, batch_size):
                if self._stop_flag:
                    return None
                    
                batch_files = files[i:i+batch_size]
                for file in batch_files:
                    if self._stop_flag:
                        return None
                        
                    file_path = os.path.join(input_dir, file)
                    try:
                        # 提取opcode
                        opcode = get_file_opcode(file_path)
                        if opcode:
                            processed_files.append(opcode)
                            self._processed_files += 1
                            # 计算当前阶段的进度
                            stage_progress = (self._processed_files / self._total_files) * progress_range
                            current_progress = start_progress + int(stage_progress)
                            progress_message = f'[INFO] 已处理 {"恶意" if is_malicious else "正常"}样本: {file}'
                            self.update_progress(current_progress, progress_message)
                    except Exception as e:
                        error_message = f'[WARNING] 处理文件 {file} 时出错: {str(e)}'
                        raise Exception(error_message)
                        
            if not processed_files:
                raise Exception(f"没有成功提取到任何特征")
                
            # 保存特征
            with open(output_file, 'wb') as f:
                pickle.dump(processed_files, f)

            return True

        except Exception as e:
            error_message = f" {str(e)}"
            raise Exception(error_message)
            
    def run(self):
        try:
            # 记录开始时间
            self.start_time = datetime.now()
            print(f"[DEBUG] 训练开始时间: {self.start_time}")
            
            # 重置进度计数
            self._total_files = 0
            self._processed_files = 0
            self._current_progress = 0
            
            # 使用数据集根目录的路径计算哈希
            dataset_root = os.path.dirname(self.malicious_dir)
            # 规范化路径，确保格式一致
            dataset_root = os.path.normpath(dataset_root)
            # 使用绝对路径
            dataset_root = os.path.abspath(dataset_root)
            # 确保路径末尾没有斜杠
            dataset_root = dataset_root.rstrip('/')
            
            self.dataset_id = hashlib.md5(dataset_root.encode('utf-8')).hexdigest()
            print(f"[DEBUG] 训练线程使用的数据集根目录: {dataset_root}")
            print(f"[DEBUG] 训练线程计算的数据集哈希: {self.dataset_id}")
            print(f"[DEBUG] 路径长度: {len(dataset_root)}")
            print(f"[DEBUG] 路径字节: {dataset_root.encode('utf-8')}")

            # 创建opcode目录
            opcode_dir = os.path.join(dataset_root, 'opcode')
            os.makedirs(opcode_dir, exist_ok=True)

            # 设置opcode文件路径
            malicious_opcode = os.path.join(opcode_dir, 'malicious.pkl')
            benign_opcode = os.path.join(opcode_dir, 'benign.pkl')

            # 检查停止标志
            if not self.is_running:
                self.stopped.emit()
                return
                
            start_message = '[INFO] 开始提取恶意样本特征...'
            self.update_progress(0, start_message)
            
            # 提取恶意样本特征
            try:
                result = self.extract_features_async(
                    self.malicious_dir,
                    malicious_opcode,
                    is_malicious=True
                )
                if result is None:  # 被停止
                    self.stopped.emit()
                    return
            except Exception as e:
                error_message = f"提取恶意样本特征失败: {str(e)}"
                self.db.save_training_log(
                    user_id=self.user_id,
                    model_name=self.model_type,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    status=error_message,
                    end_time=datetime.now(),
                    normal_dir=self.benign_dir,
                    malicious_dir=self.malicious_dir
                )
                raise Exception(error_message)
            
            # 检查停止标志
            if not self.is_running:
                self.stopped.emit()
                return
                
            start_message = '[INFO] 开始提取正常样本特征...'
            self.update_progress(40, start_message)
            
            # 提取正常样本特征
            try:
                result = self.extract_features_async(
                    self.benign_dir,
                    benign_opcode,
                    is_malicious=False
                )
                if result is None:  # 被停止
                    self.stopped.emit()
                    return
            except Exception as e:
                error_message = f"提取正常样本特征失败: {str(e)}"
                self.db.save_training_log(
                    user_id=self.user_id,
                    model_name=self.model_type,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    status=error_message,
                    end_time=datetime.now(),
                    normal_dir=self.benign_dir,
                    malicious_dir=self.malicious_dir
                )
                raise Exception(error_message)
            
            # 检查停止标志
            if not self.is_running:
                self.stopped.emit()
                return
                
            # 获取特征矩阵
            self.update_progress(80, '[INFO] 正在生成特征矩阵...')
            
            try:
                x, y = get_feature_for_train(
                    malicious_opcode,
                    benign_opcode,
                    new=True,
                    user_id=self.user_id
                )
            except Exception as e:
                error_message = f"生成特征矩阵失败: {str(e)}"
                self.db.save_training_log(
                    user_id=self.user_id,
                    model_name=self.model_type,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    status=error_message,
                    end_time=datetime.now(),
                    normal_dir=self.benign_dir,
                    malicious_dir=self.malicious_dir
                )
                raise Exception(error_message)
            
            if x is None or y is None or len(x) == 0 or len(y) == 0:
                error_message = "特征提取失败，没有足够的有效样本"
                self.db.save_training_log(
                    user_id=self.user_id,
                    model_name=self.model_type,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    status=error_message,
                    end_time=datetime.now(),
                    normal_dir=self.benign_dir,
                    malicious_dir=self.malicious_dir
                )
                raise Exception(error_message)
            
            # 检查停止标志
            if not self.is_running:
                self.stopped.emit()
                return
                
            # 开始训练模型
            self.update_progress(85, f'[INFO] 开始训练{self.model_type}模型...')
            
            try:
                model, metrics = train_model(
                    x, y,
                    self.model_type,
                    {"malicious_dir": self.malicious_dir, 
                     "benign_dir": self.benign_dir,
                     "hash": self.dataset_id,  # 传递正确的数据集ID
                     "train_start_time": self.start_time},
                    self.user_id
                )
                
                if model is None:
                    error_message = "模型训练失败"
                    self.db.save_training_log(
                        user_id=self.user_id,
                        model_name=self.model_type,
                        accuracy=0.0,
                        precision=0.0,
                        recall=0.0,
                        f1_score=0.0,
                        status=error_message,
                        end_time=datetime.now(),
                        normal_dir=self.benign_dir,
                        malicious_dir=self.malicious_dir
                    )
                    raise Exception(error_message)
                
                # 使用train_model返回的metrics
                accuracy = metrics['accuracy']
                precision = metrics['precision']
                recall = metrics['recall']
                f1 = metrics['f1_score']
                
                # 计算训练时长
                end_time = datetime.now()
                training_seconds = (end_time - self.start_time).total_seconds()
                training_time = self.format_duration(training_seconds)
                print(f"[DEBUG] 训练结束时间: {end_time}")
                print(f"[DEBUG] 计算得到的训练时长: {training_time}")
                
                # 保存训练日志
                self.db.save_training_log(
                    user_id=self.user_id,
                    model_name=self.model_type,
                    accuracy=accuracy,
                    precision=precision,
                    recall=recall,
                    f1_score=f1,
                    status="训练成功",
                    start_time=self.start_time,
                    end_time=end_time,
                    training_time=training_time,
                    normal_dir=self.benign_dir,
                    malicious_dir=self.malicious_dir
                )
                
                success_message = f'[INFO] {self.model_type}模型训练完成！'
                self.update_progress(100, success_message)
                
                # 构建metrics字符串
                metrics_str = f"accuracy={accuracy:.4f}, precision={precision:.4f}, recall={recall:.4f}, f1={f1:.4f}"
                self.finished.emit(True, metrics)
                
            except Exception as e:
                error_message = f"模型训练失败: {str(e)}"
                end_time = datetime.now()
                training_seconds = (end_time - self.start_time).total_seconds()
                training_time = self.format_duration(training_seconds)
                print(f"[DEBUG] 训练失败时间: {end_time}")
                print(f"[DEBUG] 训练失败时的训练时长: {training_time}")
                self.db.save_training_log(
                    user_id=self.user_id,
                    model_name=self.model_type,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    status=error_message,
                    start_time=self.start_time,
                    end_time=end_time,
                    training_time=training_time,
                    normal_dir=self.benign_dir,
                    malicious_dir=self.malicious_dir
                )
                raise Exception(error_message)
            
        except Exception as e:
            error_msg = f'[ERROR] 训练过程中发生错误: {str(e)}'
            self.progress.emit(error_msg)
            self.log_messages.append(error_msg)
            self.error.emit(str(e)) 

    def update_progress(self, percent, message):
        """更新进度"""
        if percent < self._current_progress:
            return  # 防止进度倒退
        self._current_progress = percent
        self.progress_percent.emit(percent)
        self.progress.emit(message)
        self.log_messages.append(message)


        