import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from View.main_window import MainWindow

def main():
    # 设置高DPI支持（必须在创建QApplication之前）
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    QApplication.setStyle('Fusion')
    
    # 设置应用程序信息
    app.setApplicationName("Webshell检测系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Webshell检测")
    
    # 创建主窗口
    window = MainWindow()
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 