from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStackedWidget, QMessageBox, QLabel,
                             QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                             QFrame)
from PyQt5.QtGui import QFont
from View.sidebar_button import SidebarButton
from View.detection_page import DetectionPage
from View.training_page import TrainingPage
from View.log_page import LogPage
from View.login_page import LoginPage
from View.model_page import ModelPage
from View.profile_page import ProfilePage
from Model.database import Database

class LoginDialog(QDialog):
    """登录对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录")
        self.setFixedSize(300, 150)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        layout.addRow("用户名:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("密码:", self.password_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addRow(button_box)
        self.setLayout(layout)
        
    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.current_user_id = None
        self.current_model = None
        self.db = Database()
        self.show_login()
        

        
    def get_user_files(self, file_type=None):
        """获取用户的文件列表"""
        if not self.current_user_id:
            return []
            
        return self.db.get_user_files(self.current_user_id, file_type)
        
    def delete_file_path(self, file_path):
        """删除文件路径记录"""
        if not self.current_user_id:
            return False
            
        success, message = self.db.delete_file_path(self.current_user_id, file_path)
        if not success:
            QMessageBox.warning(self, "错误", message)
        return success
        
    def show_login(self):
        """显示登录界面"""
        self.login_page = LoginPage()
        self.setCentralWidget(self.login_page)
        self.setWindowTitle('登录 - WebShell检测系统')
        self.setGeometry(100, 100, 1200, 800)
        
    def show_main_interface(self):
        """显示主界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建侧边栏
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-right: 1px solid #cccccc;
            }
        """)
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # 侧边栏标题
        sidebar_title = QLabel("WebShell检测系统")
        sidebar_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                padding: 20px;
                background-color: #e3f2fd;
            }
        """)
        sidebar_layout.addWidget(sidebar_title)
        
        # 侧边栏按钮
        self.training_button = SidebarButton("模型训练")
        self.training_button.setChecked(True)
        self.training_button.clicked.connect(lambda: self.switch_page(1))
        
        self.model_button = SidebarButton("模型管理")
        self.model_button.clicked.connect(self.show_model_management)

        self.detection_button = SidebarButton("Webshell检测")
        self.detection_button.clicked.connect(lambda: self.switch_page(0))
        
        self.log_button = SidebarButton("日志记录")
        self.log_button.clicked.connect(lambda: self.switch_page(2))
        
        self.profile_button = SidebarButton("个人中心")
        self.profile_button.clicked.connect(lambda: self.switch_page(3))
        
        self.about_button = SidebarButton("关于")
        self.about_button.clicked.connect(self.show_about)
        
        self.logout_button = SidebarButton("退出登录")
        self.logout_button.clicked.connect(self.logout)
        
        sidebar_layout.addWidget(self.training_button)
        sidebar_layout.addWidget(self.model_button)
        sidebar_layout.addWidget(self.detection_button)
        sidebar_layout.addWidget(self.log_button)
        sidebar_layout.addWidget(self.profile_button)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.about_button)
        sidebar_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(sidebar)
        
        # 创建堆叠部件
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #f5f5f5;
            }
        """)
        
        # 添加页面
        self.detection_page = DetectionPage(self)
        self.training_page = TrainingPage(self)
        self.log_page = LogPage(self)
        self.model_page = ModelPage(self)
        self.profile_page = ProfilePage(self)
        
        self.stacked_widget.addWidget(self.detection_page)
        self.stacked_widget.addWidget(self.training_page)
        self.stacked_widget.addWidget(self.log_page)
        self.stacked_widget.addWidget(self.profile_page)
        self.stacked_widget.addWidget(self.model_page)
        
        main_layout.addWidget(self.stacked_widget)
        
        # 设置窗口属性
        self.setWindowTitle('WebShell检测系统')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置字体
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        
    def logout(self):
        """退出登录"""
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出登录吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.show_login()
        
    def show_model_management(self):
        """显示模型管理页面"""
        self.model_page.update_models_display()    # 刷新模型列表
        self.model_page.refresh_datasets()  # 刷新数据集列表
        
        # 检查是否还有模型
        if not self.model_page.models:  # 如果没有模型了
            self.current_model = None  # 清除当前模型
            if hasattr(self, 'detection_page'):
                self.detection_page.update_model_display(None)  # 更新检测页面显示
                
        self.stacked_widget.setCurrentWidget(self.model_page)
        
    def set_current_model(self, model_info):
        """设置当前使用的模型"""
        self.current_model = model_info
        if hasattr(self, 'detection_page'):
            self.detection_page.update_model_display(model_info)
            
    def switch_page(self, index):
        """切换页面"""
        self.detection_button.setChecked(index == 0)
        self.training_button.setChecked(index == 1)
        self.log_button.setChecked(index == 2)
        self.profile_button.setChecked(index == 3)
        self.model_button.setChecked(index == 4)
        
        self.stacked_widget.setCurrentIndex(index)
        
    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h3>WebShell检测系统</h3>
        <p>基于机器学习的WebShell检测工具</p>
        <p>版本: 1.0</p>
        <p>功能:</p>
        <ul>
            <li>单文件检测</li>
            <li>目录扫描</li>
            <li>自动生成检测报告</li>
            <li>高危文件删除</li>
            <li>模型训练</li>
            <li>模型管理</li>
        </ul>
        """
        QMessageBox.about(self, "关于", about_text) 