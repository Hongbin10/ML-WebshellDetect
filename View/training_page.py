from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem,
                             QMessageBox, QLineEdit, QHeaderView, QProgressBar, QLabel, QComboBox, QTabWidget)
from PyQt5.QtCore import pyqtSignal
import os
from Controller.training_thread import TrainingThread
from Controller.processing_thread import PreprocessingThread
from Model.database import Database


class TrainingPage(QWidget):
    model_trained = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存父窗口引用
        self.db = Database()  # 初始化数据库连接
        self.preprocessing_tab = None  # 添加这行
        self.training_tab = None  # 添加这行
        self.initUI()
        self.preprocess_thread = None

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #e3f2fd;
            }
        """)

        # 创建数据预处理选项卡页面
        self.preprocessing_tab = QWidget()
        self.setup_preprocessing_tab()

        # 创建模型训练选项卡页面
        self.training_tab = QWidget()
        self.setup_training_tab()

        # 将选项卡页面添加到选项卡控件
        self.tab_widget.addTab(self.preprocessing_tab, "数据预处理")
        self.tab_widget.addTab(self.training_tab, "机器学习训练")

        main_layout.addWidget(self.tab_widget)

    def setup_preprocessing_tab(self):
        """设置预处理选项卡"""
        layout = QVBoxLayout(self.preprocessing_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 目录选择部分
        dir_layout = QVBoxLayout()
        dir_layout.setSpacing(10)

        # 恶意样本目录
        malicious_layout = QHBoxLayout()
        malicious_layout.setSpacing(10)
        self.malicious_dir_edit = QLineEdit()
        self.malicious_dir_edit.setPlaceholderText("请选择恶意样本目录...")
        self.malicious_dir_edit.setStyleSheet("""
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
        browse_malicious_btn = QPushButton('浏览目录')
        browse_malicious_btn.setStyleSheet("""
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
        browse_malicious_btn.clicked.connect(lambda: self.browse_dir(self.malicious_dir_edit))
        malicious_layout.addWidget(QLabel("恶意样本目录:"))
        malicious_layout.addWidget(self.malicious_dir_edit)
        malicious_layout.addWidget(browse_malicious_btn)
        dir_layout.addLayout(malicious_layout)

        # 正常样本目录
        benign_layout = QHBoxLayout()
        benign_layout.setSpacing(10)
        self.benign_dir_edit = QLineEdit()
        self.benign_dir_edit.setPlaceholderText("请选择正常样本目录...")
        self.benign_dir_edit.setStyleSheet("""
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
        browse_benign_btn = QPushButton('浏览目录')
        browse_benign_btn.setStyleSheet("""
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
        browse_benign_btn.clicked.connect(lambda: self.browse_dir(self.benign_dir_edit))
        benign_layout.addWidget(QLabel("正常样本目录:"))
        benign_layout.addWidget(self.benign_dir_edit)
        benign_layout.addWidget(browse_benign_btn)
        dir_layout.addLayout(benign_layout)

        # 输出目录
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("请选择输出目录...")
        self.output_dir_edit.setStyleSheet("""
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
        browse_output_btn = QPushButton('浏览目录')
        browse_output_btn.setStyleSheet("""
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
        browse_output_btn.clicked.connect(lambda: self.browse_dir(self.output_dir_edit))
        output_layout.addWidget(QLabel("输出目录:"))
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(browse_output_btn)
        dir_layout.addLayout(output_layout)

        layout.addLayout(dir_layout)

        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.start_btn = QPushButton('开始预处理')
        self.start_btn.setStyleSheet("""
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
        self.start_btn.clicked.connect(self.start_preprocessing)
        self.stop_btn = QPushButton('停止预处理')
        self.stop_btn.setStyleSheet("""
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
        self.stop_btn.clicked.connect(self.stop_preprocessing)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)



        # 日志显示
        self.preprocess_log_text = QTextEdit()
        self.preprocess_log_text.setReadOnly(True)
        self.preprocess_log_text.setMinimumHeight(150)
        self.preprocess_log_text.setStyleSheet("""
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
        layout.addWidget(self.preprocess_log_text)



    def browse_dir(self, line_edit):
        """浏览目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            line_edit.setText(dir_path)

    def start_preprocessing(self):
        """开始预处理"""
        # 验证输入
        malicious_dir = self.malicious_dir_edit.text()
        benign_dir = self.benign_dir_edit.text()
        output_dir = self.output_dir_edit.text()

        if not all([malicious_dir, benign_dir, output_dir]):
            QMessageBox.warning(self, "警告", "请选择所有必要的目录")
            return

        if not all([os.path.isdir(d) for d in [malicious_dir, benign_dir]]):
            QMessageBox.warning(self, "警告", "输入目录无效")
            return

        # 清空日志和进度
        self.preprocess_log_text.clear()  # 改为 preprocess_log_text

        # 创建并启动线程
        self.preprocess_thread = PreprocessingThread(malicious_dir, benign_dir, output_dir)
        self.preprocess_thread.progress.connect(self.update_progress)
        self.preprocess_thread.finished.connect(self.on_preprocess_finished)
        self.preprocess_thread.error.connect(self.on_preprocess_error)
        self.preprocess_thread.start()

        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_preprocessing(self):
        """停止预处理"""
        if self.preprocess_thread and self.preprocess_thread.isRunning():
            self.preprocess_thread.stop()
            # 重置按钮状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            # 更新日志
            self.preprocess_log_text.append("[INFO] 预处理已停止")
        QMessageBox.information(self, "停止", "数据预处理已停止！")

    def update_progress(self, message):
        """更新进度"""
        self.preprocess_log_text.append(message)  # 改为 preprocess_log_text
        self.preprocess_log_text.verticalScrollBar().setValue(
            self.preprocess_log_text.verticalScrollBar().maximum()
        )

    def on_preprocess_finished(self, output_dir):
        """预处理完成"""
        self.preprocess_log_text.append(f"预处理完成！输出目录: {output_dir}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.information(self, "完成", f"数据预处理完成！\n输出目录: {output_dir}")

    def on_preprocess_error(self, error_msg):
        """预处理错误"""
        self.preprocess_log_text.append(f"错误: {error_msg}")
        # 重置按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "错误", f"预处理失败: {error_msg}")

    # --- 以下是模型训练选项卡的方法 (从原 TrainingPage 迁移和调整) ---

    def setup_training_tab(self):
        """设置模型训练选项卡的UI"""
        layout = QVBoxLayout(self.training_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # --- 样本选择部分 (从原 initUI 迁移) ---
        sample_layout = QVBoxLayout()
        sample_layout.setSpacing(10)

        malicious_layout = QHBoxLayout()
        malicious_layout.setSpacing(10)
        self.malicious_path_input = QLineEdit()
        self.malicious_path_input.setPlaceholderText("请选择恶意样本目录...")
        self.malicious_path_input.setStyleSheet("""
            QLineEdit { padding: 8px; border: 1px solid #cccccc; border-radius: 4px; background-color: white; }
            QLineEdit:focus { border-color: #2196F3; }
        """)
        malicious_browse_button = QPushButton('浏览目录')
        malicious_browse_button.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; padding: 8px 15px; border: none; border-radius: 4px; min-width: 80px; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        malicious_browse_button.clicked.connect(self.browse_malicious_dir)
        malicious_layout.addWidget(QLabel("恶意样本目录:"))
        malicious_layout.addWidget(self.malicious_path_input)
        malicious_layout.addWidget(malicious_browse_button)

        benign_layout = QHBoxLayout()
        benign_layout.setSpacing(10)
        self.benign_path_input = QLineEdit()
        self.benign_path_input.setPlaceholderText("请选择正常样本目录...")
        self.benign_path_input.setStyleSheet("""
            QLineEdit { padding: 8px; border: 1px solid #cccccc; border-radius: 4px; background-color: white; }
            QLineEdit:focus { border-color: #2196F3; }
        """)
        benign_browse_button = QPushButton('浏览目录')
        benign_browse_button.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; padding: 8px 15px; border: none; border-radius: 4px; min-width: 80px; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        benign_browse_button.clicked.connect(self.browse_benign_dir)
        benign_layout.addWidget(QLabel("正常样本目录:"))
        benign_layout.addWidget(self.benign_path_input)
        benign_layout.addWidget(benign_browse_button)

        sample_layout.addLayout(malicious_layout)
        sample_layout.addLayout(benign_layout)
        layout.addLayout(sample_layout)

        # --- 模型选择部分 (从原 initUI 迁移) ---
        model_label = QLabel("选择模型类型:")
        model_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(model_label)
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["XGBoost", "随机森林", "决策树", "SVM", "朴素贝叶斯"])  # 更新模型类型选项
        self.model_type_combo.setStyleSheet("""
            QComboBox { padding: 8px; border: 1px solid #cccccc; border-radius: 4px; background-color: white; min-width: 300px; min-height: 35px; }
            QComboBox::drop-down { border: none; width: 35px; }
            QComboBox::down-arrow { image: url(down_arrow.png); width: 12px; height: 12px; }
            QComboBox QAbstractItemView { border: 1px solid #cccccc; selection-background-color: #e3f2fd; selection-color: #0D47A1; background-color: white; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding: 8px 12px; margin: 0; }
            QComboBox QAbstractItemView::item:hover { background-color: #f5f5f5; }
            QComboBox QAbstractItemView::item:selected { background-color: #e3f2fd; color: #0D47A1; }
        """)
        layout.addWidget(self.model_type_combo)

        # --- 训练控制按钮 (从原 initUI 迁移) ---
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        self.train_button = QPushButton('开始训练')
        self.train_button.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; padding: 8px 15px; border: none; border-radius: 4px; min-width: 100px; }
            QPushButton:hover { background-color: #388E3C; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.train_button.clicked.connect(self.start_training)
        self.stop_button = QPushButton('停止训练')
        self.stop_button.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; padding: 8px 15px; border: none; border-radius: 4px; min-width: 100px; }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.stop_button.clicked.connect(self.stop_training)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.train_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        # --- 进度条 (从原 initUI 迁移) ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #cccccc; border-radius: 4px; text-align: center; height: 20px; }
            QProgressBar::chunk { background-color: #4CAF50; border-radius: 3px; }
        """)
        layout.addWidget(self.progress_bar)

        # --- 训练日志显示 (从原 initUI 迁移) ---
        self.training_log_text = QTextEdit()
        self.training_log_text.setReadOnly(True)
        self.training_log_text.setMinimumHeight(150)
        self.training_log_text.setStyleSheet("""
            QTextEdit { border: 1px solid #cccccc; border-radius: 4px; padding: 8px; background-color: white; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; line-height: 1.4; }
        """)
        layout.addWidget(self.training_log_text)

        # --- 评估结果表格 ---
        self.result_table = QTableWidget()
        self.result_table.setMinimumHeight(200)
        self.result_table.setColumnCount(4)  # 修改列数为3
        self.result_table.setHorizontalHeaderLabels(['开始时间', '结束时间', '模型名称', '准确率'])  # 修改表头
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 开始时间列宽固定
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 结束时间列宽固定
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 模型名称列自适应宽度
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 准确率列自适应宽度
        self.result_table.setColumnWidth(0, 200)  # 设置开始时间列宽
        self.result_table.setColumnWidth(1, 200)  # 设置结束时间列宽
        self.result_table.setColumnWidth(2, 200)  # 设置模型名称列宽
        self.result_table.setColumnWidth(3, 200)  # 设置准确率列宽
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
        """)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.result_table)

    def browse_malicious_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self.training_tab, "选择恶意样本目录") # 父窗口改为self.training_tab
        if dir_path:
            self.malicious_path_input.setText(dir_path)

    def browse_benign_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self.training_tab, "选择正常样本目录") # 父窗口改为self.training_tab
        if dir_path:
            self.benign_path_input.setText(dir_path)

    def start_training(self):
        """开始训练"""
        malicious_dir = self.malicious_path_input.text()
        benign_dir = self.benign_path_input.text()
        model_type = self.model_type_combo.currentText()

        if not malicious_dir or not benign_dir:
            QMessageBox.warning(self.training_tab, "警告", "请选择样本目录！")
            return

        # 检查两个目录是否在同一父目录下
        malicious_parent = os.path.dirname(os.path.abspath(malicious_dir))
        benign_parent = os.path.dirname(os.path.abspath(benign_dir))
        
        if malicious_parent != benign_parent:
            QMessageBox.warning(
                self.training_tab, 
                "警告", 
                "恶意样本和正常样本必须在同一目录下！\n\n"
                f"当前恶意样本: {malicious_dir}\n"
                f"当前正常样本: {benign_dir}\n\n"
                f"请将两个数据集放到 {malicious_parent} 目录下 或者 {benign_parent} 目录下。"
            )
            return

        # 清空日志
        self.training_log_text.clear()
        self.progress_bar.setValue(0)

        # 获取当前用户ID
        if not hasattr(self.main_window, 'current_user_id'):
            QMessageBox.warning(self.training_tab, "错误", "未获取到用户ID，请重新登录")
            return
        user_id = self.main_window.current_user_id
        self.training_log_text.append(f"[INFO] 当前用户ID: {user_id}")

        # 保存数据集信息
        success, message, dataset_id = self.main_window.db.save_dataset(
            user_id=user_id,
            normal_dir=benign_dir,
            malicious_dir=malicious_dir
        )
        
        if not success:
            QMessageBox.warning(self.training_tab, "错误", f"保存数据集信息失败: {message}")
            return
        
        self.training_log_text.append(f"[INFO] {message}")
        self.training_log_text.append(f"[INFO] 数据集ID: {dataset_id}")

        # 创建训练线程
        self.training_thread = TrainingThread(
            malicious_dir=malicious_dir, 
            benign_dir=benign_dir, 
            model_type=model_type, 
            user_id=user_id, 
            dataset_id=dataset_id
        )
        self.training_thread.progress.connect(self.update_training_progress)
        self.training_thread.progress_percent.connect(self.update_progress_bar)
        self.training_thread.finished.connect(self.handle_training_finished)
        self.training_thread.error.connect(self.handle_training_error)
        self.training_thread.stopped.connect(self.handle_training_stopped)

        # 更新按钮状态
        self.train_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # 开始训练
        self.training_thread.start()

    def stop_training(self):
        """停止训练"""
        reply = QMessageBox.question(
            self.training_tab, # 父窗口改为self.training_tab
            '确认停止',
            '确定要停止训练吗？已完成的训练结果将被保存。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if hasattr(self, 'training_thread') and self.training_thread is not None and self.training_thread.isRunning():
                # 发送停止信号
                self.training_thread.stop()

                # 更新界面状态
                self.train_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.progress_bar.setValue(0)  # 进度条归零
                self.training_log_text.append('[INFO] 正在停止训练...')

                # 等待线程结束 (可以考虑移除或添加超时)
                # self.training_thread.wait() # wait可能导致UI卡死，谨慎使用

                self.training_log_text.append('[INFO] 训练已停止')
                QMessageBox.information(self, "停止", f"模型训练已停止！")
            else:
                 self.training_log_text.append('[INFO] 训练尚未开始或已结束')
                 self.train_button.setEnabled(True)
                 self.stop_button.setEnabled(False)

    def update_training_progress(self, message):
        """更新训练进度信息"""
        self.training_log_text.append(message)

    def update_progress_bar(self, value):
        """更新训练进度条"""
        self.progress_bar.setValue(value)

    def handle_training_finished(self, result, metrics):
        """处理训练完成事件"""
        # 更新界面状态
        self.train_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)

        # 获取当前用户ID
        if not hasattr(self.main_window, 'current_user_id'):
            QMessageBox.warning(self.training_tab, "错误", "未获取到用户ID，请重新登录")
            return
        user_id = self.main_window.current_user_id

        # 获取最新的训练记录
        training_logs = self.db.get_training_logs(user_id)
        if training_logs and len(training_logs) > 0:
            latest_log = training_logs[0]  # 获取最新的记录
            
            # 清空表格
            self.result_table.setRowCount(0)
            
            # 添加新行
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            
            # 解包日志数据 (根据数据库表结构)
            (log_id, start_time, end_time, model_name,
             accuracy, precision, recall, f1_score, status,
             normal_dir, malicious_dir, training_time) = latest_log
            
            # 设置数据
            self.result_table.setItem(row, 0, QTableWidgetItem(str(start_time)))  # 开始时间
            self.result_table.setItem(row, 1, QTableWidgetItem(str(end_time if end_time else "未完成")))  # 结束时间
            self.result_table.setItem(row, 2, QTableWidgetItem(model_name))  # 模型名称
            self.result_table.setItem(row, 3, QTableWidgetItem(f"{accuracy:.4f}"))  # 准确率
            
        # 发送模型训练完成信号
        self.model_trained.emit()
        QMessageBox.information(self, "完成", "模型训练完成！\n")

    def handle_training_error(self, error_message):
        """处理训练错误"""

        self.train_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.training_log_text.append(f"[ERROR] {error_message}")
        QMessageBox.critical(self.training_tab, "训练错误", error_message) # 父窗口改为self.training_tab

    def handle_training_stopped(self):
        """处理训练停止"""
        self.train_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.training_log_text.append("[INFO] 训练已停止")

