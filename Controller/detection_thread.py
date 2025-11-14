from PyQt5.QtCore import QThread, pyqtSignal
import joblib
from Model.detect import extract_opcodes_for_detect, get_feature_from_loaded_model
import shutil
from Utils.utils import *

class DetectionThread(QThread):
    """检测线程"""
    progress = pyqtSignal(str)
    progress_percent = pyqtSignal(int)
    error = pyqtSignal(str)
    finished = pyqtSignal(dict, dict, dict)
    
    def __init__(self, dest_dir, remove_flag, model_path=None):
        super().__init__()
        self.dest_dir = dest_dir
        self.remove_flag = remove_flag
        self.model_path = model_path
        self.log_messages = []  # 存储日志消息

    def run(self):
        try:
            # 生成报告文件名和路径
            fn = get_time().replace(':', '') + '.html'
            output_path = os.path.join('../gui/report_template', fn)
            
            # 初始化报告
            report = {
                'cmdline': f'python3 Detect.py -o {output_path} {self.dest_dir}',
                'start_time': get_time()
            }
            
            # 加载模型
            if self.model_path and os.path.exists(self.model_path):
                model = joblib.load(self.model_path)
            else:
                self.error.emit("未找到模型文件")
                return
                
            # 加载特征提取器
            features_dir = os.path.dirname(os.path.dirname(self.model_path))
            cv_path = os.path.join(features_dir, 'features', 'cv_model.pkl')
            tfidf_path = os.path.join(features_dir, 'features', 'tfidf_model.pkl')
            
            if not os.path.exists(cv_path) or not os.path.exists(tfidf_path):
                self.error.emit("未找到特征提取器文件")
                return
                
            cv = joblib.load(cv_path)
            tfidf = joblib.load(tfidf_path)
            
            # 检测文件
            result = {}
            vuln = {}
            
            if os.path.isfile(self.dest_dir):
                # 单文件检测
                self.log_messages.append(f'[INFO] 检测文件: {self.dest_dir}')
                self.progress.emit(f"正在检测文件: {self.dest_dir}")
                self.progress_percent.emit(50)
                
                # 提取特征
                fps, opcodes = extract_opcodes_for_detect(self.dest_dir)
                if not fps:
                    self.error.emit(f"无法提取文件特征: {self.dest_dir}")
                    return
                    
                # 转换特征
                x_detect = get_feature_from_loaded_model(cv, tfidf, opcodes)
                
                # 预测
                pred = model.predict(x_detect)[0]
                result[self.dest_dir] = pred
                if pred == 1:
                    vuln[self.dest_dir] = {
                        'label': '1'
                    }
                    
                self.progress_percent.emit(100)
                
            else:
                # 目录扫描
                php_files = []
                for root, _, files in os.walk(self.dest_dir):
                    for file in files:
                        if file.endswith('.php'):
                            php_files.append(os.path.join(root, file))
                            
                total_files = len(php_files)
                for i, file_path in enumerate(php_files):
                    self.progress.emit(f"正在检测文件: {file_path} ({i+1}/{total_files})")
                    self.progress_percent.emit(int((i+1)/total_files * 100))
                    
                    # 提取特征
                    fps, opcodes = extract_opcodes_for_detect(file_path)
                    if not fps:
                        continue
                        
                    # 转换特征
                    x_detect = get_feature_from_loaded_model(cv, tfidf, opcodes)
                    
                    # 预测
                    pred = model.predict(x_detect)[0]
                    result[file_path] = pred
                    if pred == 1:
                        vuln[file_path] = {
                            'label': '1'
                        }
            
            # 更新报告信息
            report['end_time'] = get_time()
            report['file_count'] = str(len(result))
            report['vuln_count'] = str(len(vuln))
            
            # 添加文件详细信息到漏洞结果
            for fp in vuln.keys():
                vul = vuln[fp]
                vul['fsize'] = get_file_size(fp)
                vul['flast'] = get_file_last_modify(fp)
                try:
                    # 尝试不同的编码方式读取文件
                    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
                    for encoding in encodings:
                        try:
                            with open(fp, 'r', encoding=encoding) as f:
                                vul['fcode'] = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # 如果所有编码都失败，使用二进制模式读取
                        with open(fp, 'rb') as f:
                            content = f.read()
                            try:
                                vul['fcode'] = content.decode('utf-8', errors='replace')
                            except:
                                vul['fcode'] = "文件内容包含无法解码的字符"
                except Exception as e:
                    vul['fcode'] = f"无法读取文件内容: {str(e)}"
                vuln[fp] = vul
                self.log_messages.append(f'[WARN] 发现恶意文件: {fp}')
            
            if self.remove_flag:
                shutil.rmtree(self.dest_dir)
                self.log_messages.append(f'[INFO] 已删除目录: {self.dest_dir}')
            
            self.finished.emit(result, vuln, report)
            
        except Exception as e:
            error_msg = f'[ERROR] 检测过程中发生错误: {str(e)}'
            self.progress.emit(error_msg)
            self.log_messages.append(error_msg)
            self.error.emit(str(e)) 