from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox,
                             QLabel, QFrame, QGridLayout, QScrollArea, QComboBox)
from Model.database import Database
import os

class ModelCard(QFrame):
    """模型卡片组件"""
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.parent_page = parent  # 保存父页面的引用
        self.setObjectName("modelCard")
        self.setStyleSheet("""
            #modelCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 10px;
            }
            #modelCard:hover {
                border-color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 模型标题和时间
        title_layout = QHBoxLayout()
        model_title = QLabel(f"{model['model_type']} v{model['version']}")
        model_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333;
        """)
        title_layout.addWidget(model_title)
        
        # 添加生成时间
        if model.get('created_at'):
            time_label = QLabel(f"生成时间: {model['created_at']}")
            time_label.setStyleSheet("color: #666666; font-size: 12px;")
            title_layout.addWidget(time_label)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 数据集信息
        dataset_layout = QVBoxLayout()
        dataset_layout.setSpacing(5)
        
        # 添加数据集路径信息
        if model.get('normal_dir') and model.get('malicious_dir'):
            normal_dir_label = QLabel(f"正常样本目录: {model['normal_dir']}")
            malicious_dir_label = QLabel(f"恶意样本目录: {model['malicious_dir']}")
            
            normal_dir_label.setStyleSheet("color: #666666; font-size: 12px;")
            malicious_dir_label.setStyleSheet("color: #666666; font-size: 12px;")
            
            # 设置文本自动换行
            normal_dir_label.setWordWrap(True)
            malicious_dir_label.setWordWrap(True)
            
            dataset_layout.addWidget(normal_dir_label)
            dataset_layout.addWidget(malicious_dir_label)
        
        layout.addLayout(dataset_layout)
        
        # 模型指标
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(10)
        
        metrics = [
            ("准确率", f"{model['accuracy']*100:.2f}%"),
            ("精确率", f"{model['precision']:.4f}"),
            ("召回率", f"{model['recall']:.4f}"),
            ("F1分数", f"{model['f1_score']:.4f}")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_label = QLabel(label)
            metric_label.setStyleSheet("color: #666666;")
            metric_value = QLabel(value)
            metric_value.setStyleSheet("color: #2196F3; font-weight: bold;")
            
            metrics_layout.addWidget(metric_label, i//2, (i%2)*2)
            metrics_layout.addWidget(metric_value, i//2, (i%2)*2+1)
        
        layout.addLayout(metrics_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("选择模型")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        select_btn.clicked.connect(lambda: self.parent_page.select_model(self.model))
        
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #f44336;
                border: 1px solid #f44336;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f44336;
                color: white;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
                color: white;
            }
        """)
        delete_btn.clicked.connect(lambda: self.parent_page.delete_model(self.model))
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)

class StatsCard(QFrame):
    """统计信息卡片组件"""
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setObjectName("statsCard")
        self.setStyleSheet("""
            #statsCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #666666; font-size: 12px;")
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #2196F3; font-size: 20px; font-weight: bold;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        """设置统计值"""
        self.value_label.setText(value)

class ModelPage(QWidget):
    """模型管理页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.db = Database()
        self.models = []  # 添加models属性
        self.current_model_id = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 页面标题
        title_label = QLabel("模型管理")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title_label)

        # 当前模型状态显示
        self.current_model_label = QLabel("当前使用模型：未选择")
        self.current_model_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-weight: bold;
                padding: 15px;
                background-color: #e3f2fd;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        main_layout.addWidget(self.current_model_label)

        # 统计信息区域
        stats_layout = QHBoxLayout()
        self.stats_cards = [
            StatsCard("总模型数", "0"),
            StatsCard("最高准确率", "0%"),
            StatsCard("平均F1分数", "0.00")
        ]
        for card in self.stats_cards:
            stats_layout.addWidget(card)
        main_layout.addLayout(stats_layout)

        # 数据集选择和工具栏
        toolbar_layout = QHBoxLayout()
        
        # 数据集选择框
        self.dataset_combo = QComboBox()
        self.dataset_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
                color: #333333;
            }
            QComboBox:hover {
                border-color: #2196F3;
                background-color: #f5f5f5;
            }
            QComboBox:focus {
                border-color: #2196F3;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                background-color: white;
                selection-background-color: #e3f2fd;
                selection-color: #2196F3;
                padding: 4px;
            }
        """)
        self.dataset_combo.currentIndexChanged.connect(self.filter_models_by_dataset)
        toolbar_layout.addWidget(QLabel("选择数据集："))
        toolbar_layout.addWidget(self.dataset_combo)
        
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # 模型卡片容器
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.refresh_datasets()
        self.update_models_display()

    def refresh_datasets(self):
        """刷新数据集列表"""
        self.dataset_combo.clear()
        self.dataset_combo.addItem("所有数据集")
        
        # 从数据库获取所有数据集
        datasets = self.db.get_all_datasets()
        # 获取所有有模型的dataset_id
        models = self.db.get_all_models()
        model_dataset_ids = {model['dataset_id'] for model in models}
        
        # 只显示有模型的dataset_id对应的数据集
        for dataset in datasets:
            if dataset['dataset_id'] in model_dataset_ids:
                # 从normal_dir中提取数据集目录名称
                normal_dir = dataset['normal_dir']
                dataset_name = os.path.basename(os.path.dirname(normal_dir))
                self.dataset_combo.addItem(dataset_name, dataset['dataset_id'])
        
        # 如果没有数据集有模型，显示提示信息
        if self.dataset_combo.count() == 1:  # 只有"所有数据集"选项
            self.dataset_combo.addItem("暂无可用数据集")
            self.dataset_combo.setEnabled(False)
        else:
            self.dataset_combo.setEnabled(True)

    def filter_models_by_dataset(self, index):
        """根据选择的数据集过滤模型"""
        if index == 0:  # 选择"所有数据集"
            # 获取当前用户的所有模型
            self.models = self.db.get_user_models(self.main_window.current_user_id)
        else:
            # 获取指定数据集的所有模型
            dataset_id = self.dataset_combo.itemData(index)
            all_models = self.db.get_models_by_dataset(dataset_id)
            # 过滤出当前用户的模型
            self.models = [model for model in all_models if model['user_id'] == self.main_window.current_user_id]
        
        # 更新UI显示
        self.update_models_display()
        
    def update_models_display(self):
        """更新模型显示"""
        # 清除现有卡片
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加模型卡片
        for i, model in enumerate(self.models):
            card = ModelCard(model, self)
            row = i // 2  # 计算行号
            col = i % 2   # 计算列号
            self.cards_layout.addWidget(card, row, col)
        
        # 添加弹性空间
        self.cards_layout.setRowStretch(self.cards_layout.rowCount(), 1)
        
        # 更新统计信息
        total_models = len(self.models)
        max_accuracy = max((model['accuracy'] for model in self.models), default=0) * 100
        avg_f1 = sum(model['f1_score'] for model in self.models) / total_models if total_models > 0 else 0
        
        self.stats_cards[0].set_value(str(total_models))
        self.stats_cards[1].set_value(f"{max_accuracy:.2f}%")
        self.stats_cards[2].set_value(f"{avg_f1:.4f}")

    def select_model(self, model):
        """选择当前模型"""
        # 检查模型是否属于当前用户
        if model['user_id'] != self.main_window.current_user_id:
            QMessageBox.warning(self, "错误", "您没有权限使用此模型")
            return
            
        self.current_model_id = model['model_id']
        self.current_model_label.setText(
            f"当前使用模型：{model['model_type']} v{model['version']} | "
            f"准确率: {model['accuracy']*100:.1f}% | "
            f"F1分数: {model['f1_score']:.2f}"
        )
        self.main_window.set_current_model(model)
        QMessageBox.information(self, "成功", f"已选择模型：{model['model_type']} v{model['version']}")

    def delete_model(self, model):
        """删除模型及其相关文件"""
        reply = QMessageBox.question(
            self, 
            '确认删除',
            f'确定要删除模型 {model["model_type"]} v{model["version"]} 吗？\n',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除模型文件
                if os.path.exists(model['model_path']):
                    os.remove(model['model_path'])
                
                # 删除特征文件
                if model.get('dataset_id'):
                    # 检查该数据集是否还有其他模型在使用
                    all_models = self.db.get_user_models(self.main_window.current_user_id)
                    other_models = [m for m in all_models if m['dataset_id'] == model['dataset_id'] and m['model_id'] != model['model_id']]
                    
                    # 如果没有其他模型使用该数据集，则删除特征文件
                    if not other_models:
                        feature_models = self.db.get_feature_models(model['dataset_id'])
                        for feature_model in feature_models:
                            # 删除特征文件
                            for path in [feature_model['cv_path'], feature_model['tfidf_path'],
                                       feature_model['matrix_path'], feature_model['labels_path'],
                                       feature_model['malicious_opcode_path'], feature_model['benign_opcode_path']]:
                                if path and os.path.exists(path):
                                    os.remove(path)
                            
                            # 删除特征模型记录
                            self.db.delete_feature_model(feature_model['feature_id'])
                
                # 删除机器学习模型记录
                self.db.delete_ml_model(model['model_id'])
                
                # 检查是否是当前使用的模型
                if self.current_model_id == model['model_id']:
                    self.current_model_id = None
                    self.current_model_label.setText("当前使用模型：未选择")
                    self.main_window.set_current_model(None)
                
                self.update_models_display()  # 刷新模型列表
                self.refresh_datasets()  # 刷新数据集列表
                
                # 根据是否有其他模型显示不同的提示信息
                if 'other_models' in locals() and not other_models:
                    QMessageBox.information(self, "成功", "模型及其特征文件已删除")
                else:
                    QMessageBox.information(self, "成功", "模型已删除，但仍有其他模型使用该数据集")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除模型时发生错误：\n{str(e)}") 