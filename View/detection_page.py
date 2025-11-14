from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem,
                             QMessageBox, QLineEdit, QHeaderView, QStackedWidget,
                             QProgressBar, QLabel, QMainWindow)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import os
from Controller.detection_thread import DetectionThread
from Utils.utils import get_time, get_file_size, get_file_last_modify
from Utils.report import generate_report
from Model.detect import delete_files
from datetime import datetime

class DetectionPage(QWidget):
    """检测页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.detection_thread = None
        self.current_result = None
        self.current_vuln = None
        self.current_report = None
        self.current_report_path = None
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加模型状态显示
        self.model_status_label = QLabel("当前检测模型：未选择")
        self.model_status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 10px;
                font-size: 13px;
                border-bottom: 1px solid #eeeeee;
            }
        """)
        layout.addWidget(self.model_status_label)
        
        # 检测模式切换按钮组
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        
        self.single_file_button = QPushButton("单文件检测")
        self.single_file_button.setCheckable(True)
        self.single_file_button.setChecked(True)
        self.single_file_button.clicked.connect(lambda: self.switch_mode(0))
        
        self.directory_button = QPushButton("目录扫描")
        self.directory_button.setCheckable(True)
        self.directory_button.clicked.connect(lambda: self.switch_mode(1))
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                padding: 8px 15px;
                border: 1px solid #cccccc;
                background-color: white;
                color: #333333;
                font-size: 13px;
                min-width: 100px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:checked {
                background-color: #e3f2fd;
                border-color: #2196F3;
                color: #0D47A1;
            }
        """
        self.single_file_button.setStyleSheet(button_style)
        self.directory_button.setStyleSheet(button_style)
        
        mode_layout.addWidget(self.single_file_button)
        mode_layout.addWidget(self.directory_button)
        mode_layout.addStretch()
        
        layout.addLayout(mode_layout)
        
        # 创建堆叠部件用于切换不同的检测模式
        self.stacked_widget = QStackedWidget()
        
        # 单文件检测页面
        single_file_page = QWidget()
        single_file_layout = QVBoxLayout(single_file_page)
        single_file_layout.setContentsMargins(0, 10, 0, 0)
        
        file_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("请选择要检测的PHP文件...")
        self.file_path_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        browse_file_button = QPushButton('浏览文件')
        browse_file_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        browse_file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(browse_file_button)
        
        single_file_layout.addLayout(file_layout)
        
        # 目录扫描页面
        directory_page = QWidget()
        directory_layout = QVBoxLayout(directory_page)
        directory_layout.setContentsMargins(0, 10, 0, 0)
        
        folder_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setPlaceholderText("请选择要扫描的目录...")
        self.folder_path_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        browse_folder_button = QPushButton('浏览目录')
        browse_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        browse_folder_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_path_input)
        folder_layout.addWidget(browse_folder_button)
        
        directory_layout.addLayout(folder_layout)
        
        # 添加页面到堆叠部件
        self.stacked_widget.addWidget(single_file_page)
        self.stacked_widget.addWidget(directory_page)
        
        layout.addWidget(self.stacked_widget)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.detect_button = QPushButton('开始检测')
        self.detect_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.detect_button.clicked.connect(self.start_detection)
        
        self.report_button = QPushButton('检测报告')
        self.report_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.report_button.clicked.connect(self.open_report)
        self.report_button.setEnabled(False)  # 初始状态禁用
        
        self.delete_files_button = QPushButton('删除高危文件')
        self.delete_files_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.delete_files_button.clicked.connect(self.delete_vuln_files)
        self.delete_files_button.setEnabled(False)  # 初始状态禁用
        
        button_layout.addWidget(self.detect_button)
        button_layout.addWidget(self.report_button)
        button_layout.addWidget(self.delete_files_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 检测进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 检测过程显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setMinimumHeight(300)
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['文件路径', '检测结果', '文件大小', '最后修改时间'])
        
        # 设置表格列宽
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # 文件路径列自适应宽度
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)    # 检测结果列固定宽度
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)    # 文件大小列固定宽度
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)    # 最后修改时间列固定宽度
        
        # 设置固定列宽
        self.result_table.setColumnWidth(1, 100)  # 检测结果列宽
        self.result_table.setColumnWidth(2, 100)  # 文件大小列宽
        self.result_table.setColumnWidth(3, 160)  # 最后修改时间列宽
        
        self.result_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #0D47A1;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-right: 1px solid #cccccc;
                border-bottom: 1px solid #cccccc;
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #fafafa;
            }
        """)
        
        # 启用交替行颜色
        self.result_table.setAlternatingRowColors(True)
        
        # 设置表格选择模式
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.result_table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择
        
        layout.addWidget(self.result_table)
        
        self.setLayout(layout)
        
    def switch_mode(self, index):
        """切换检测模式"""
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.single_file_button.setChecked(True)
            self.directory_button.setChecked(False)
        else:
            self.single_file_button.setChecked(False)
            self.directory_button.setChecked(True)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择PHP文件",
            "",
            "PHP Files (*.php);;All Files (*)"
        )
        if file_path:
            if not file_path.lower().endswith('.php'):
                QMessageBox.warning(self, "警告", "请选择PHP文件！")
                return
            self.file_path_input.setText(file_path)
            self.folder_path_input.clear()
            


    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if folder_path:
            self.folder_path_input.setText(folder_path)
            self.file_path_input.clear()


    def start_detection(self):
        # 检查是否已选择模型
        if not self.window().current_model:
            QMessageBox.warning(self, "警告", "请先在模型管理页面选择检测模型！")
            return
        
        # 获取当前模型信息
        current_model = self.window().current_model
        model_path = current_model.get('model_path')
        
        # 检查模型文件是否存在
        if not model_path or not os.path.exists(model_path):
            QMessageBox.warning(self, "警告", f"模型文件不存在：{model_path}")
            return
        
        # 检查是否选择了文件或目录
        file_path = self.file_path_input.text()
        folder_path = self.folder_path_input.text()
        
        if not file_path and not folder_path:
            QMessageBox.warning(self, "警告", "请先选择文件或目录！")
            return
            
        # 确定检测目标
        dest_dir = file_path if file_path else folder_path
        remove_flag = False
        
       
        self.log_text.clear()
        self.progress_bar.setValue(0)
        
        # 创建并启动检测线程
        self.detection_thread = DetectionThread(
            dest_dir=dest_dir, 
            remove_flag=remove_flag,
            model_path=model_path
        )
        
        # 打印调试信息
        self.log_text.append(f"[DEBUG] 使用模型：{current_model['model_type']} v{current_model['version']}")
        self.log_text.append(f"[DEBUG] 模型路径：{model_path}")
        
        self.detection_thread.progress.connect(self.update_progress)
        self.detection_thread.progress_percent.connect(self.update_progress_bar)
        self.detection_thread.error.connect(self.handle_error)
        self.detection_thread.finished.connect(self.handle_result)
        self.detection_thread.start()
        
        # 禁用检测按钮
        self.detect_button.setEnabled(False)
        self.detect_button.setText("检测中...")
        
    def update_progress(self, message):
        self.log_text.append(message)
        
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
        
    def handle_error(self, error_message):
        """处理检测错误"""
        QMessageBox.critical(self, "错误", f"检测过程中发生错误：\n{error_message}")
        self.log_text.append(f"错误：{error_message}")
        
        # 记录错误日志
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            input_data = self.file_path_input.text() or self.folder_path_input.text()
            input_name = os.path.basename(input_data) if input_data else "未知文件"
            
            # 生成错误报告文件名
            report_name = f'error_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            report_path = os.path.join('../Data/report', report_name)
            
            # 确保report目录存在
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            # 获取当前选择的模型信息
            model_info = main_window.current_model
            model_name = model_info['model_type'] if model_info else "未选择模型"
            
            main_window.db.save_detection_log(
                main_window.current_user_id,
                input_data,  # 检测文件路径
                input_name,  # 检测文件名
                "失败",  # 检测结果
                f"检测失败：{error_message}",  # 详细结果
                report_path,  # 报告路径
                report_name,  # 报告文件名
                model_name,  # 模型名称
                "失败",  # 状态
                detect_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        
        # 恢复检测按钮
        self.detect_button.setEnabled(True)
        self.detect_button.setText("开始检测")

    def handle_result(self, result, vuln, report):
        """处理检测结果"""
        self.current_result = result
        self.current_vuln = vuln
        self.current_report = report

        # 更新结果表格
        self.result_table.setRowCount(len(result))
        for i, (file_path, label) in enumerate(result.items()):
            self.result_table.setItem(i, 0, QTableWidgetItem(file_path.replace(os.getcwd(), '.')))
            self.result_table.setItem(i, 1, QTableWidgetItem("正常" if label == 0 else "高危"))
            
            if os.path.exists(file_path):
                fsize = get_file_size(file_path)
                flast = get_file_last_modify(file_path)
            else:
                fsize = "文件已删除"
                flast = "文件已删除"
            
            self.result_table.setItem(i, 2, QTableWidgetItem(fsize))
            self.result_table.setItem(i, 3, QTableWidgetItem(flast))
        
        has_dangerous_files = any(label == 1 for label in result.values())
        # 启用删除高危文件按钮
        self.delete_files_button.setEnabled(has_dangerous_files)
        # 自动生成报告
        try:
            # 生成报告文件名和路径
            report_name = f'report_{get_time().replace(":", "")}.html'
            report_path = os.path.join('../Data/report', report_name)
            
            # 确保report目录存在
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            # 生成报告
            generate_report(self.current_report, self.current_result, self.current_vuln, report_path)
            self.current_report_path = report_path
            
            # 保存检测日志
            main_window = self.window()
            if isinstance(main_window, QMainWindow):
                input_path = self.file_path_input.text() or self.folder_path_input.text()
                input_name = os.path.basename(input_path)
                
                # 确定整体检测结果
                overall_result = "高危" if any(label == 1 for label in result.values()) else "正常"
                
                # 生成详细的检测结果统计信息
                result_details = f"从 {len(result)} 个PHP文件中发现 {len(vuln)} 个恶意文件"
                
                main_window.db.save_detection_log(
                    main_window.current_user_id,
                    input_path,
                    input_name,
                    overall_result,
                    result_details,
                    report_path,
                    report_name,
                    "XGBoost",  # 当前使用的检测模型名称
                    "成功",
                    detect_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # 启用报告按钮
            self.report_button.setEnabled(True)
            
            self.log_text.append(f'[INFO] 检测报告已生成: {report_path}')
            
        except Exception as e:
            self.log_text.append(f'[ERROR] 生成报告失败: {str(e)}')

        self.log_text.append(f'[INFO] 从 {len(result)} 个PHP文件中发现 {len(vuln)} 个恶意文件。')
        
        # 恢复检测按钮
        self.detect_button.setEnabled(True)
        self.detect_button.setText("开始检测")

    def open_report(self):
        """打开检测报告"""
        if self.current_report_path and os.path.exists(self.current_report_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(self.current_report_path)))
        else:
            QMessageBox.warning(self, "警告", "检测报告文件不存在！")

    def delete_vuln_files(self):
        if not self.current_vuln:
            QMessageBox.warning(self, "警告", "请先进行检测！")
            return

        vuln_file_paths = [k for k, v in self.current_vuln.items() if v['label'] == '1']
        if not vuln_file_paths:
            self.log_text.append("[INFO] 未检测到高危文件，无需删除操作。")
            return

        reply = QMessageBox.question(self, '确认删除',
                                     f'确定要删除 {len(vuln_file_paths)} 个高危文件吗？',
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # 执行删除操作
                delete_files(vuln_file_paths)

                # 将绝对路径转换为表格中使用的相对路径格式
                relative_vuln_paths = {p.replace(os.getcwd(), '.') for p in vuln_file_paths}

                # 查找需要删除的行
                rows_to_remove = []
                for row in range(self.result_table.rowCount()):
                    item = self.result_table.item(row, 0)
                    if item and item.text() in relative_vuln_paths:
                        rows_to_remove.append(row)

                # 从后往前删除行，避免索引错乱
                for row in sorted(rows_to_remove, reverse=True):
                    self.result_table.removeRow(row)

                # self.result_table.setRowCount(0) # 不再清空表格

                self.log_text.append("[INFO] 高危文件已删除")
                self.delete_files_button.setEnabled(False) # 删除成功后禁用按钮
                QMessageBox.information(self, "成功", "高危文件已删除")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除文件时发生错误：\n{str(e)}")
                self.log_text.append(f'[ERROR] 删除文件时发生错误: {str(e)}')

    def update_model_display(self, model_info):
        """更新模型显示"""
        if model_info is None:
            display_text = "当前检测模型：未选择"
        else:
            display_text = (
                f"当前检测模型：{model_info['model_type']} v{model_info['version']} | "
                f"准确率: {model_info['accuracy']*100:.1f}% | "
                f"F1分数: {model_info['f1_score']:.2f}"
            )
        self.model_status_label.setText(display_text) 