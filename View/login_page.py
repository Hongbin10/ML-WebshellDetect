from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QStackedWidget, QMainWindow)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Model.database import Database
import re

class LoginPage(QWidget):
    """登陆页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.initUI()

    def initUI(self):
        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧装饰面板
        left_panel = QWidget()
        left_panel.setFixedWidth(500)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #1a73e8;
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # 左侧标题
        title_label = QLabel("WebShell检测系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 36, QFont.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        left_layout.addWidget(title_label)
        
        # 左侧副标题
        subtitle_label = QLabel("专业的WebShell检测解决方案")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Microsoft YaHei", 16))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        left_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(left_panel)
        
        # 右侧登录面板
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 60, 60, 60)
        right_layout.setSpacing(25)
        
        # 创建堆叠部件用于切换登录和注册页面
        self.stacked_widget = QStackedWidget()
        
        # 创建登录页面
        login_widget = QWidget()
        login_layout = QVBoxLayout()
        login_layout.setSpacing(25)
        
        # 登录标题
        login_title = QLabel("欢迎登录")
        login_title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        login_title.setStyleSheet("color: #1a73e8;")
        login_layout.addWidget(login_title)
        
        # 用户名输入
        username_label = QLabel("用户名")
        username_label.setFont(QFont("Microsoft YaHei", 12))
        username_label.setStyleSheet("color: #5f6368;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setMinimumHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        login_layout.addWidget(username_label)
        login_layout.addWidget(self.username_input)
        
        # 密码输入
        password_label = QLabel("密码")
        password_label.setFont(QFont("Microsoft YaHei", 12))
        password_label.setStyleSheet("color: #5f6368;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password_input)
        
        # 登录按钮
        login_button = QPushButton("登 录")
        login_button.setMinimumHeight(50)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self.handle_login)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #174ea6;
            }
        """)
        login_layout.addWidget(login_button)
        
        # 切换到注册页面的按钮
        switch_to_register = QPushButton("没有账号？立即注册")
        switch_to_register.setCursor(Qt.PointingHandCursor)
        switch_to_register.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #1557b0;
            }
        """)
        switch_to_register.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        login_layout.addWidget(switch_to_register)
        
        # 添加忘记密码按钮
        forgot_password = QPushButton("忘记密码？")
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #1557b0;
            }
        """)
        forgot_password.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        login_layout.addWidget(forgot_password)
        
        login_layout.addStretch()
        login_widget.setLayout(login_layout)
        
        # 创建注册页面
        register_widget = QWidget()
        register_layout = QVBoxLayout()
        register_layout.setSpacing(25)
        
        # 注册标题
        register_title = QLabel("用户注册")
        register_title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        register_title.setStyleSheet("color: #1a73e8;")
        register_layout.addWidget(register_title)
        
        # 注册用户名输入
        register_username_label = QLabel("用户名")
        register_username_label.setFont(QFont("Microsoft YaHei", 12))
        register_username_label.setStyleSheet("color: #5f6368;")
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("请输入用户名")
        self.register_username.setMinimumHeight(50)
        self.register_username.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        register_layout.addWidget(register_username_label)
        register_layout.addWidget(self.register_username)
        
        # 添加邮箱输入
        email_label = QLabel("邮箱")
        email_label.setFont(QFont("Microsoft YaHei", 12))
        email_label.setStyleSheet("color: #5f6368;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入邮箱")
        self.email_input.setMinimumHeight(50)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        register_layout.addWidget(email_label)
        register_layout.addWidget(self.email_input)
        
        # 注册密码输入
        register_password_label = QLabel("密码")
        register_password_label.setFont(QFont("Microsoft YaHei", 12))
        register_password_label.setStyleSheet("color: #5f6368;")
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("请输入密码")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setMinimumHeight(50)
        self.register_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        register_layout.addWidget(register_password_label)
        register_layout.addWidget(self.register_password)
        
        # 确认密码输入
        confirm_password_label = QLabel("确认密码")
        confirm_password_label.setFont(QFont("Microsoft YaHei", 12))
        confirm_password_label.setStyleSheet("color: #5f6368;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("请再次输入密码")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setMinimumHeight(50)
        self.confirm_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        register_layout.addWidget(confirm_password_label)
        register_layout.addWidget(self.confirm_password)
        
        # 注册按钮
        register_button = QPushButton("注 册")
        register_button.setMinimumHeight(50)
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.clicked.connect(self.register)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #174ea6;
            }
        """)
        register_layout.addWidget(register_button)
        
        # 切换到登录页面的按钮
        switch_to_login = QPushButton("已有账号？立即登录")
        switch_to_login.setCursor(Qt.PointingHandCursor)
        switch_to_login.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #1557b0;
            }
        """)
        switch_to_login.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        register_layout.addWidget(switch_to_login)
        
        register_layout.addStretch()
        register_widget.setLayout(register_layout)
        
        # 创建忘记密码页面
        forgot_password_widget = QWidget()
        forgot_password_layout = QVBoxLayout()
        forgot_password_layout.setSpacing(25)
        
        # 忘记密码标题
        forgot_title = QLabel("找回密码")
        forgot_title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        forgot_title.setStyleSheet("color: #1a73e8;")
        forgot_password_layout.addWidget(forgot_title)
        
        # 用户名输入
        forgot_username_label = QLabel("用户名")
        forgot_username_label.setFont(QFont("Microsoft YaHei", 12))
        forgot_username_label.setStyleSheet("color: #5f6368;")
        self.forgot_username = QLineEdit()
        self.forgot_username.setPlaceholderText("请输入用户名")
        self.forgot_username.setMinimumHeight(50)
        self.forgot_username.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        forgot_password_layout.addWidget(forgot_username_label)
        forgot_password_layout.addWidget(self.forgot_username)
        
        # 邮箱输入
        forgot_email_label = QLabel("邮箱")
        forgot_email_label.setFont(QFont("Microsoft YaHei", 12))
        forgot_email_label.setStyleSheet("color: #5f6368;")
        self.forgot_email = QLineEdit()
        self.forgot_email.setPlaceholderText("请输入注册邮箱")
        self.forgot_email.setMinimumHeight(50)
        self.forgot_email.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        forgot_password_layout.addWidget(forgot_email_label)
        forgot_password_layout.addWidget(self.forgot_email)
        
        # 新密码输入
        new_password_label = QLabel("新密码")
        new_password_label.setFont(QFont("Microsoft YaHei", 12))
        new_password_label.setStyleSheet("color: #5f6368;")
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("请输入新密码")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setMinimumHeight(50)
        self.new_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        forgot_password_layout.addWidget(new_password_label)
        forgot_password_layout.addWidget(self.new_password)
        
        # 确认新密码输入
        confirm_new_password_label = QLabel("确认新密码")
        confirm_new_password_label.setFont(QFont("Microsoft YaHei", 12))
        confirm_new_password_label.setStyleSheet("color: #5f6368;")
        self.confirm_new_password = QLineEdit()
        self.confirm_new_password.setPlaceholderText("请再次输入新密码")
        self.confirm_new_password.setEchoMode(QLineEdit.Password)
        self.confirm_new_password.setMinimumHeight(50)
        self.confirm_new_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8eaed;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        forgot_password_layout.addWidget(confirm_new_password_label)
        forgot_password_layout.addWidget(self.confirm_new_password)
        
        # 重置密码按钮
        reset_button = QPushButton("重置密码")
        reset_button.setMinimumHeight(50)
        reset_button.setCursor(Qt.PointingHandCursor)
        reset_button.clicked.connect(self.reset_password)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #174ea6;
            }
        """)
        forgot_password_layout.addWidget(reset_button)
        
        # 返回登录页面的按钮
        back_to_login = QPushButton("返回登录")
        back_to_login.setCursor(Qt.PointingHandCursor)
        back_to_login.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #1557b0;
            }
        """)
        back_to_login.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        forgot_password_layout.addWidget(back_to_login)
        
        forgot_password_layout.addStretch()
        forgot_password_widget.setLayout(forgot_password_layout)
        
        # 添加页面到堆叠部件
        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)
        self.stacked_widget.addWidget(forgot_password_widget)
        
        right_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码！")
            return
            
        # 验证用户名和密码
        success, message, user_id = self.db.verify_user(username, password)
        
        if success:
            # 直接进入系统，不显示成功提示
            main_window = self.window()
            if isinstance(main_window, QMainWindow):
                main_window.current_user_id = user_id
                main_window.show_main_interface()
        else:
            QMessageBox.critical(self, "错误", message)

    def register(self):
        username = self.register_username.text()
        email = self.email_input.text()
        password = self.register_password.text()
        confirm = self.confirm_password.text()
        
        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "警告", "请填写所有字段")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
            
        # 验证邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            QMessageBox.warning(self, "警告", "请输入有效的邮箱地址")
            return
            
        success, message = self.db.register_user(username, password, email)
        if success:
            QMessageBox.information(self, "成功", message)
            self.stacked_widget.setCurrentIndex(0)  # 切换到登录页面
        else:
            QMessageBox.warning(self, "错误", message)

    def reset_password(self):
        """重置密码"""
        username = self.forgot_username.text()
        email = self.forgot_email.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_new_password.text()
        
        if not username or not email or not new_password or not confirm_password:
            QMessageBox.warning(self, "警告", "请填写所有字段")
            return
            
        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
            
        # 验证用户名和邮箱
        success, message, user_id = self.db.verify_user_email(username, email)
        if not success:
            QMessageBox.warning(self, "错误", message)
            return
            
        # 重置密码
        success, message = self.db.reset_password(user_id, new_password)
        if success:
            QMessageBox.information(self, "成功", message)
            self.stacked_widget.setCurrentIndex(0)  # 切换到登录页面
            # 清空输入框
            self.forgot_username.clear()
            self.forgot_email.clear()
            self.new_password.clear()
            self.confirm_new_password.clear()
        else:
            QMessageBox.warning(self, "错误", message) 