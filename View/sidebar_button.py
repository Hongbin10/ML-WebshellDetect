from PyQt5.QtWidgets import QPushButton, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import os

class SidebarButton(QPushButton):
    """侧边栏按钮类"""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 20px;
                border: none;
                background-color: transparent;
                color: #333333;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
                color: #0D47A1;
            }
        """)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24)) 