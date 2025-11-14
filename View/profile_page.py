from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Model.database import Database

class ProfilePage(QWidget):
    """个人中心页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.initUI()
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # 减小间距
        main_layout.setContentsMargins(20, 20, 20, 20)  # 减小边距
        
        # 标题
        title = QLabel("个人中心")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))  # 减小字体大小
        title.setStyleSheet("color: #1a73e8;")
        main_layout.addWidget(title)
        
        # 创建修改密码区域
        password_frame = QFrame()
        password_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        password_layout = QVBoxLayout(password_frame)
        password_layout.setSpacing(10)
        
        # 修改密码标题
        password_title = QLabel("修改密码")
        password_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        password_title.setStyleSheet("color: #333333;")
        password_layout.addWidget(password_title)
        
        # 邮箱输入
        email_label = QLabel("邮箱")
        email_label.setFont(QFont("Microsoft YaHei", 11))
        email_label.setStyleSheet("color: #5f6368;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入注册邮箱")
        self.email_input.setMinimumHeight(35)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 4px;
                padding: 0 10px;
                font-size: 13px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        password_layout.addWidget(email_label)
        password_layout.addWidget(self.email_input)
        
        # 新密码输入
        new_password_label = QLabel("新密码")
        new_password_label.setFont(QFont("Microsoft YaHei", 11))
        new_password_label.setStyleSheet("color: #5f6368;")
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("请输入新密码")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setMinimumHeight(35)
        self.new_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 4px;
                padding: 0 10px;
                font-size: 13px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        password_layout.addWidget(new_password_label)
        password_layout.addWidget(self.new_password)
        
        # 确认新密码输入
        confirm_password_label = QLabel("确认新密码")
        confirm_password_label.setFont(QFont("Microsoft YaHei", 11))
        confirm_password_label.setStyleSheet("color: #5f6368;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("请再次输入新密码")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setMinimumHeight(35)
        self.confirm_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 4px;
                padding: 0 10px;
                font-size: 13px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        password_layout.addWidget(confirm_password_label)
        password_layout.addWidget(self.confirm_password)
        
        # 修改密码按钮
        change_password_button = QPushButton("修改密码")
        change_password_button.setMinimumHeight(35)
        change_password_button.setCursor(Qt.PointingHandCursor)
        change_password_button.clicked.connect(self.change_password)
        change_password_button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #174ea6;
            }
        """)
        password_layout.addWidget(change_password_button)
        
        main_layout.addWidget(password_frame)
        
        # 创建用户注销区域
        delete_frame = QFrame()
        delete_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        delete_layout = QVBoxLayout(delete_frame)
        delete_layout.setSpacing(10)  # 减小间距
        
        # 用户注销标题
        delete_title = QLabel("用户注销")
        delete_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        delete_title.setStyleSheet("color: #333333;")
        delete_layout.addWidget(delete_title)
        
        # 警告信息
        warning_label = QLabel("警告：注销账号将删除所有与该用户相关的数据，包括检测日志、训练日志、数据集和模型。此操作不可恢复！")
        warning_label.setWordWrap(True)
        warning_label.setFont(QFont("Microsoft YaHei", 11))
        warning_label.setStyleSheet("color: #d93025;")
        delete_layout.addWidget(warning_label)
        
        # 添加密码输入框
        password_label = QLabel("请输入登录密码")
        password_label.setFont(QFont("Microsoft YaHei", 11))
        password_label.setStyleSheet("color: #5f6368;")
        self.delete_password = QLineEdit()
        self.delete_password.setPlaceholderText("请输入登录密码")
        self.delete_password.setEchoMode(QLineEdit.Password)
        self.delete_password.setMinimumHeight(35)
        self.delete_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 4px;
                padding: 0 10px;
                font-size: 13px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        delete_layout.addWidget(password_label)
        delete_layout.addWidget(self.delete_password)
        
        # 注销按钮
        delete_button = QPushButton("注销账号")
        delete_button.setMinimumHeight(35)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(self.delete_account)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d93025;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b31412;
            }
            QPushButton:pressed {
                background-color: #8a0000;
            }
        """)
        delete_layout.addWidget(delete_button)
        
        main_layout.addWidget(delete_frame)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def change_password(self):
        """修改密码"""
        email = self.email_input.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        if not email or not new_password or not confirm_password:
            QMessageBox.warning(self, "警告", "请填写所有字段")
            return
            
        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
            
        # 获取当前用户的邮箱
        success, message, user_email = self.db.get_user_email(self.window().current_user_id)
        if not success:
            QMessageBox.warning(self, "错误", message)
            return
            
        # 验证邮箱是否匹配
        if email != user_email:
            QMessageBox.warning(self, "错误", "邮箱输入错误，请确认后重试")
            return
            
        # 重置密码
        success, message = self.db.reset_password(self.window().current_user_id, new_password)
        if success:
            QMessageBox.information(self, "成功", message)
            self.window().show_login()  # 返回登录页面
        else:
            QMessageBox.warning(self, "错误", message)
            
    def delete_account(self):
        """删除账号"""
        # 获取当前用户ID和密码
        current_user_id = self.window().current_user_id
        password = self.delete_password.text()
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入登录密码")
            return
            
        # 验证密码
        success, message = self.db.verify_user_password(current_user_id, password)
        if not success:
            QMessageBox.warning(self, "错误", message)
            return
            
        reply = QMessageBox.question(self, '确认注销', 
                                   '确定要注销账号吗？此操作将删除所有与该用户相关的数据，且不可恢复！',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除用户数据
            success, message = self.db.delete_user_data(current_user_id)
            if success:
                QMessageBox.information(self, "成功", message)
                self.window().show_login()  # 返回登录页面
            else:
                QMessageBox.warning(self, "错误", message) 