from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTextEdit, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QLabel, QMainWindow, QTabWidget, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import os
import sqlite3
from Model.database import Database  # 添加Database导入


class LogPage(QWidget):
    """日志页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存父窗口引用
        self.db = Database()  # 初始化数据库连接
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 创建选项卡
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 15px;
                margin-right: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background: #f5f5f5;
            }
            QTabBar::tab:selected {
                background: white;
                margin-bottom: -1px;
            }
            QTabBar::tab:hover {
                background: #e3f2fd;
            }
        """)

        # 检测日志选项卡
        detection_tab = QWidget()
        detection_layout = QVBoxLayout(detection_tab)

        # 检测日志表格
        self.detection_table = QTableWidget()
        self.detection_table.setColumnCount(7)  # 修改列数
        self.detection_table.setHorizontalHeaderLabels([
            '时间', '检测对象', '检测结果', '使用模型', '状态', '详细信息', '操作'
        ])

        # 设置表格选择模式
        self.detection_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.detection_table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择

        # 设置默认行高
        self.detection_table.verticalHeader().setDefaultSectionSize(40)  # 增加行高
        # 设置表格列宽
        header = self.detection_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        self.detection_table.setColumnWidth(0, 180)  # 时间列
        self.detection_table.setColumnWidth(2, 150)  # 结果列
        self.detection_table.setColumnWidth(3, 100)  # 模型列
        self.detection_table.setColumnWidth(4, 80)  # 状态列
        self.detection_table.setColumnWidth(5, 100)  # 详细信息列
        self.detection_table.setColumnWidth(6, 80)  # 操作列

        self.detection_table.setStyleSheet("""
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

        detection_layout.addWidget(self.detection_table)

        # 训练日志选项卡
        training_tab = QWidget()
        training_layout = QVBoxLayout(training_tab)

        # 训练日志表格
        self.training_table = QTableWidget()
        self.training_table.setColumnCount(7)  # 增加操作列
        self.training_table.setHorizontalHeaderLabels(['开始时间', '结束时间', '模型名称', '准确率', '状态', '详细信息', '操作'])

        # 设置表格选择模式
        self.training_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.training_table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择

        # 设置默认行高
        self.training_table.verticalHeader().setDefaultSectionSize(40)  # 增加行高
        # 设置表格列宽
        header = self.training_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        self.training_table.setColumnWidth(0, 180)  # 开始时间列
        self.training_table.setColumnWidth(1, 180)  # 结束时间列
        self.training_table.setColumnWidth(2, 120)  # 模型名称列
        self.training_table.setColumnWidth(4, 80)  # 状态列
        self.training_table.setColumnWidth(5, 100)  # 详细信息列
        self.training_table.setColumnWidth(6, 80)  # 操作列

        self.training_table.setStyleSheet("""
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

        training_layout.addWidget(self.training_table)

        # 添加选项卡
        tab_widget.addTab(detection_tab, "检测日志")
        tab_widget.addTab(training_tab, "训练日志")

        layout.addWidget(tab_widget)

        # 刷新按钮
        refresh_button = QPushButton("刷新日志")
        refresh_button.setStyleSheet("""
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
        """)
        refresh_button.clicked.connect(self.refresh_logs)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def refresh_logs(self):
        """刷新日志"""
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            print(f"当前用户ID: {main_window.current_user_id}")
            
            # 获取训练日志
            training_logs = main_window.db.get_training_logs(main_window.current_user_id)
            print(f"获取到的训练日志数量: {len(training_logs)}")
            for i, log in enumerate(training_logs):
                print(f"日志{i}: {log}")
            
            self.training_table.setRowCount(len(training_logs))
            for i, log in enumerate(training_logs):
                try:
                    (log_id, start_time, end_time, model_name, 
                     accuracy, precision, recall, f1_score, status,
                     normal_dir, malicious_dir, training_time) = log
                    
                    # 设置基本信息
                    self.training_table.setItem(i, 0, QTableWidgetItem(str(start_time)))
                    self.training_table.setItem(i, 1, QTableWidgetItem(str(end_time) if end_time else "未完成"))
                    self.training_table.setItem(i, 2, QTableWidgetItem(str(model_name)))
                    
                    # 显示准确率，格式化为百分比
                    try:
                        accuracy_value = float(accuracy)
                        accuracy_item = QTableWidgetItem(f"{accuracy_value*100:.2f}%")
                        accuracy_item.setData(Qt.UserRole, accuracy_value)
                    except (ValueError, TypeError):
                        accuracy_item = QTableWidgetItem("N/A")
                    self.training_table.setItem(i, 3, accuracy_item)
                    
                    self.training_table.setItem(i, 4, QTableWidgetItem(str(status)))
                    
                    # 添加详细信息按钮
                    details_btn = QPushButton("查看")
                    details_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 8px;
                        }
                        QPushButton:hover {
                            background-color: #1976D2;
                        }
                    """)
                    
                    # 使用log_id作为第一个参数
                    details_data = (log_id, start_time, end_time, training_time, model_name, 
                                  accuracy, precision, recall, f1_score, status)
                    details_btn.clicked.connect(
                        lambda checked, data=details_data: self.show_training_details(data)
                    )
                    
                    # 添加删除按钮
                    delete_btn = QPushButton("删除")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 8px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """)
                    delete_btn.clicked.connect(
                        lambda checked, id=log_id: self.delete_training_log(id)
                    )
                    
                    # 创建按钮容器
                    details_widget = QWidget()
                    details_layout = QHBoxLayout(details_widget)
                    details_layout.setContentsMargins(4, 0, 4, 0)
                    details_layout.addWidget(details_btn)
                    self.training_table.setCellWidget(i, 5, details_widget)
                    
                    delete_widget = QWidget()
                    delete_layout = QHBoxLayout(delete_widget)
                    delete_layout.setContentsMargins(4, 0, 4, 0)
                    delete_layout.addWidget(delete_btn)
                    self.training_table.setCellWidget(i, 6, delete_widget)
                except Exception as e:
                    print(f"处理训练日志 {i} 时出错: {e}")
                    print(f"日志数据: {log}")

            # 获取检测日志
            detection_logs = main_window.db.get_detection_logs(main_window.current_user_id)
            self.detection_table.setRowCount(len(detection_logs))
            for i, log in enumerate(detection_logs):
                (log_id, detect_time, detect_file_path, detect_file_name,
                 detect_result, report_path, report_name, model_name, status) = log

                # 设置基本信息
                self.detection_table.setItem(i, 0, QTableWidgetItem(detect_time))
                self.detection_table.setItem(i, 1, QTableWidgetItem(detect_file_name))
                self.detection_table.setItem(i, 2, QTableWidgetItem(detect_result))
                self.detection_table.setItem(i, 3, QTableWidgetItem(model_name))
                self.detection_table.setItem(i, 4, QTableWidgetItem(status))

                # 添加详细信息按钮
                details_btn = QPushButton("查看")
                details_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                details_btn.clicked.connect(lambda checked, data=(
                    detect_time, detect_file_path, detect_file_name,
                    detect_result, report_path, report_name, model_name, status
                ): self.show_detection_details(data))

                # 添加删除按钮
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, log_id=log_id: self.delete_detection_log(log_id))

                # 创建按钮容器
                details_widget = QWidget()
                details_layout = QHBoxLayout(details_widget)
                details_layout.setContentsMargins(4, 0, 4, 0)
                details_layout.addWidget(details_btn)
                self.detection_table.setCellWidget(i, 5, details_widget)

                delete_widget = QWidget()
                delete_layout = QHBoxLayout(delete_widget)
                delete_layout.setContentsMargins(4, 0, 4, 0)
                delete_layout.addWidget(delete_btn)
                self.detection_table.setCellWidget(i, 6, delete_widget)

    def show_detection_details(self, data):
        """显示检测日志详细信息"""
        (detect_time, detect_file_path, detect_file_name,
         detect_result, report_path, report_name, model_name, status) = data

        # 获取详细的检测结果统计信息
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            conn = sqlite3.connect(main_window.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT detect_result_details
                FROM detection_logs
                WHERE detect_time = ? AND detect_file_path = ?
            ''', (detect_time, detect_file_path))
            result = cursor.fetchone()
            conn.close()

            result_details = result[0] if result else "无详细信息"

        details = f"""
时间：{detect_time}
检测对象：{detect_file_name}
文件路径：{detect_file_path}
检测结果：{detect_result}
检测详情：{result_details}
使用模型：{model_name}
状态：{status}
报告文件：{report_name}
"""
        # 创建一个自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("检测日志详细信息")
        dialog.setMinimumSize(800, 600)  # 设置最小尺寸
        
        # 设置窗口样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QTextEdit {
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                font-size: 14px;
                line-height: 1.5;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)  # 设置边距
        layout.setSpacing(15)  # 设置控件间距

        # 添加标题
        title_label = QLabel("检测日志详细信息")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        # 添加详细信息文本
        text_edit = QTextEdit()
        text_edit.setPlainText(details)
        text_edit.setReadOnly(True)
        text_edit.setMinimumHeight(400)  # 设置最小高度
        layout.addWidget(text_edit)

        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 添加弹性空间

        # 添加打开报告按钮
        if os.path.exists(report_path):
            open_report_btn = QPushButton("打开检测报告")
            open_report_btn.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(report_path)))
            )
            button_layout.addWidget(open_report_btn)

        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # 设置对话框为模态
        dialog.setModal(True)
        
        # 显示对话框
        dialog.exec_()

    def show_training_details(self, data):
        """显示训练日志详细信息"""
        try:
            # 获取日志ID
            log_id = data[0]  # 假设data的第一个元素是日志ID
            print(f"[DEBUG] 显示训练日志详情，log_id: {log_id}")
            
            # 获取详细信息
            details = self.db.get_training_log_details(log_id)
            if not details:
                QMessageBox.warning(self, "错误", "获取训练日志详情失败")
                return
                
            # 构建显示内容
            text = f"""
开始时间：{details['start_time']}
结束时间：{details['end_time'] or '无'}
训练时间：{details['training_time']}
模型名称：{details['model_name']}
正常样本目录：{details['normal_dir']}
恶意样本目录：{details['malicious_dir']}
准确率：{details['accuracy']:.4f}
精确率：{details['precision']:.4f}
召回率：{details['recall']:.4f}
F1分数：{details['f1_score']:.4f}
状态：{details['status']}
"""
            # 创建一个自定义对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("训练日志详细信息")
            dialog.setMinimumSize(800, 600)  # 设置最小尺寸
            
            # 设置窗口样式
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QTextEdit {
                    font-family: "Microsoft YaHei", "SimHei", sans-serif;
                    font-size: 14px;
                    line-height: 1.5;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 100px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)  # 设置边距
            layout.setSpacing(15)  # 设置控件间距

            # 添加标题
            title_label = QLabel("训练日志详细信息")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)

            # 添加详细信息文本
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            text_edit.setReadOnly(True)
            text_edit.setMinimumHeight(400)  # 设置最小高度
            layout.addWidget(text_edit)

            # 添加按钮布局
            button_layout = QHBoxLayout()
            button_layout.addStretch()  # 添加弹性空间

            # 添加关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            # 设置对话框为模态
            dialog.setModal(True)
            
            # 显示对话框
            dialog.exec_()
        except Exception as e:
            print(f"[ERROR] 显示训练日志详情时出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"显示训练日志详情失败: {str(e)}")

    def delete_detection_log(self, log_id):
        """删除检测日志"""
        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除这条检测日志吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            main_window = self.window()
            if isinstance(main_window, QMainWindow):
                success, message = main_window.db.delete_detection_log(
                    main_window.current_user_id,
                    log_id
                )
                if success:
                    self.refresh_logs()
                    QMessageBox.information(self, "成功", message)
                else:
                    QMessageBox.warning(self, "错误", message)

    def delete_training_log(self, log_id):
        """删除训练日志"""
        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除这条训练日志吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            main_window = self.window()
            if isinstance(main_window, QMainWindow):
                success, message = main_window.db.delete_training_log(
                    main_window.current_user_id,
                    log_id
                )
                if success:
                    self.refresh_logs()
                    QMessageBox.information(self, "成功", message)
                else:
                    QMessageBox.warning(self, "错误", message)

    def showEvent(self, event):
        """当页面显示时刷新日志"""
        super().showEvent(event)
        self.refresh_logs()