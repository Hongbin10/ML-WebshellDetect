import sqlite3
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self):
        # 确保data目录存在
        if not os.path.exists('Data'):
            os.makedirs('Data')
        
        self.db_path = 'Data/users.db'
        self.init_database()

    def init_database(self):
        """初始化数据库，创建用户表和文件路径表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建检测日志表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                detect_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                detect_file_path TEXT NOT NULL,
                detect_file_name TEXT NOT NULL,
                detect_result TEXT NOT NULL,
                detect_result_details TEXT NOT NULL,
                report_path TEXT NOT NULL,
                report_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建训练日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                training_time INTEGER DEFAULT 0,
                model_name TEXT NOT NULL,
                accuracy REAL NOT NULL,
                precision REAL NOT NULL,
                recall REAL NOT NULL,
                f1_score REAL NOT NULL,
                status TEXT NOT NULL,
                normal_dir TEXT,
                malicious_dir TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建数据集表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                normal_dir TEXT NOT NULL,
                malicious_dir TEXT NOT NULL,
                normal_count INTEGER NOT NULL DEFAULT 0,
                malicious_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 创建特征模型表（简化版本）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_models (
                feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                features_dir TEXT NOT NULL,
                cv_path TEXT NOT NULL,
                tfidf_path TEXT NOT NULL,
                matrix_path TEXT NOT NULL,
                labels_path TEXT NOT NULL,
                malicious_opcode_path TEXT,
                benign_opcode_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 创建机器学习模型表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_models (
                model_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                model_type TEXT NOT NULL,
                version INTEGER NOT NULL,
                f1_score REAL NOT NULL,
                precision REAL NOT NULL,
                recall REAL NOT NULL,
                accuracy REAL NOT NULL,
                model_path TEXT NOT NULL,
                feature_id INTEGER,
                training_time INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (feature_id) REFERENCES feature_models(feature_id)
            )
        ''')
        
        # 为ml_models表创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ml_models_dataset_type_f1 
            ON ml_models(dataset_id, model_type, f1_score DESC)
        ''')
        
        # 检查并添加normal_dir和malicious_dir列到training_logs表
        try:
            cursor.execute("ALTER TABLE training_logs ADD COLUMN normal_dir TEXT")
            cursor.execute("ALTER TABLE training_logs ADD COLUMN malicious_dir TEXT")
        except sqlite3.OperationalError as e:
            # 如果列已存在，忽略错误
            if "duplicate column name" not in str(e):
                print(f"[WARNING] 添加列时出错: {str(e)}")
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """对密码进行哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email):
        """注册新用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户名是否已存在
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return False, "用户名已存在"
            
            # 检查邮箱是否已存在
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return False, "邮箱已存在"
            
            hashed_password = self.hash_password(password)
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                         (username, hashed_password, email))
            
            conn.commit()
            conn.close()
            return True, "注册成功"
        except Exception as e:
            return False, f"注册失败: {str(e)}"

    def verify_user(self, username, password):
        """验证用户登录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?',
                         (username, hashed_password))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, "登录成功", result[0]  # 返回用户ID
            return False, "用户名或密码错误", None
        except Exception as e:
            return False, f"登录失败: {str(e)}", None

    def verify_user_email(self, username, email):
        """验证用户名和邮箱是否匹配"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ? AND email = ?',
                         (username, email))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, "验证成功", result[0]  # 返回用户ID
            return False, "用户名或邮箱不匹配", None
        except Exception as e:
            return False, f"验证失败: {str(e)}", None

    def reset_password(self, user_id, new_password):
        """重置用户密码"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(new_password)
            cursor.execute('UPDATE users SET password = ? WHERE id = ?',
                         (hashed_password, user_id))
            
            conn.commit()
            conn.close()
            return True, "密码重置成功"
        except Exception as e:
            return False, f"密码重置失败: {str(e)}"

    def save_detection_log(self, user_id, detect_file_path, detect_file_name, detect_result, 
                         detect_result_details, report_path, report_name, model_name, status="成功", detect_time=None):
        """保存检测日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if detect_time is None:
                detect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO detection_logs (
                    user_id, detect_file_path, detect_file_name, detect_result,
                    detect_result_details, report_path, report_name, model_name, status, detect_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, detect_file_path, detect_file_name, detect_result,
                 detect_result_details, report_path, report_name, model_name, status, detect_time))
            
            conn.commit()
            conn.close()
            return True, "检测日志保存成功"
        except Exception as e:
            return False, f"保存检测日志失败: {str(e)}"

    def save_training_log(self, user_id, model_name, accuracy, precision, recall, f1_score, status, start_time=None, end_time=None, training_time=None, normal_dir=None, malicious_dir=None):
        """保存训练日志"""
        try:
            # 确保时间格式正确
            if start_time is None:
                start_time = datetime.now()
            elif isinstance(start_time, str):
                start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                
            if end_time is None:
                end_time = datetime.now()
            elif isinstance(end_time, str):
                end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                
            # 如果没有提供训练时长，则计算
            if training_time is None:
                seconds = (end_time - start_time).total_seconds()
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                training_time = f"{int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒"
                print(f"[DEBUG] 计算训练时长: {training_time}")
            
            # 插入训练日志
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_logs 
                (user_id, model_name, accuracy, precision, recall, f1_score, status, start_time, end_time, training_time, normal_dir, malicious_dir)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, model_name, accuracy, precision, recall, f1_score, status, 
                  start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                  end_time.strftime('%Y-%m-%d %H:%M:%S'), 
                  training_time, normal_dir, malicious_dir))
            conn.commit()
            conn.close()
            print(f"[DEBUG] 训练日志保存成功，训练时长: {training_time}")
            return True
        except Exception as e:
            print(f"[错误] 保存训练日志失败: {str(e)}")
            return False

    def delete_detection_log(self, user_id, log_id):
        """删除检测日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM detection_logs 
                WHERE user_id = ? AND id = ?
            ''', (user_id, log_id))
            
            conn.commit()
            conn.close()
            return True, "检测日志删除成功"
        except Exception as e:
            return False, f"删除检测日志失败: {str(e)}"

    def delete_training_log(self, user_id, log_id):
        """删除训练日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM training_logs 
                WHERE user_id = ? AND id = ?
            ''', (user_id, log_id))
            
            conn.commit()
            conn.close()
            return True, "训练日志删除成功"
        except Exception as e:
            return False, f"删除训练日志失败: {str(e)}"

    def get_detection_logs(self, user_id, limit=50):
        """获取用户的检测日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, detect_time, detect_file_path, detect_file_name, 
                       detect_result, report_path, report_name, model_name, status
                FROM detection_logs
                WHERE user_id = ?
                ORDER BY detect_time DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            return []

    def get_training_logs(self, user_id=None):
        """获取训练日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT id, start_time, end_time, model_name, 
                           accuracy, precision, recall, f1_score, status,
                           normal_dir, malicious_dir, training_time
                    FROM training_logs 
                    WHERE user_id = ?
                    ORDER BY start_time DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, start_time, end_time, model_name, 
                           accuracy, precision, recall, f1_score, status,
                           normal_dir, malicious_dir, training_time
                    FROM training_logs 
                    ORDER BY start_time DESC
                ''')
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"获取训练日志时出错: {e}")
            return []

    def calculate_dataset_hash(self, normal_dir, malicious_dir):
        """计算数据集的哈希值"""
        # 使用数据集根目录的路径计算哈希
        dataset_root = os.path.dirname(malicious_dir)
        # 规范化路径，确保格式一致
        dataset_root = os.path.normpath(dataset_root)
        # 使用绝对路径
        dataset_root = os.path.abspath(dataset_root)
        # 确保路径末尾没有斜杠
        dataset_root = dataset_root.rstrip('/')
        
        dataset_hash = hashlib.md5(dataset_root.encode('utf-8')).hexdigest()
        print(f"[DEBUG] 数据库使用的数据集根目录: {dataset_root}")
        print(f"[DEBUG] 数据库计算的数据集哈希: {dataset_hash}")
        print(f"[DEBUG] 路径长度: {len(dataset_root)}")
        print(f"[DEBUG] 路径字节: {dataset_root.encode('utf-8')}")
        return dataset_hash

    def save_dataset(self, user_id, normal_dir, malicious_dir):
        """保存数据集记录"""
        try:
            # 计算样本数量
            normal_count = sum(1 for f in os.listdir(normal_dir) if f.endswith('.php'))
            malicious_count = sum(1 for f in os.listdir(malicious_dir) if f.endswith('.php'))
            
            # 计算数据集哈希ID
            dataset_id = self.calculate_dataset_hash(normal_dir, malicious_dir)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute('SELECT dataset_id FROM datasets WHERE dataset_id = ?', (dataset_id,))
            if cursor.fetchone():
                conn.close()
                return True, "数据集已存在", dataset_id
            
            # 插入新记录
            cursor.execute('''
                INSERT INTO datasets (dataset_id, user_id, normal_dir, malicious_dir, normal_count, malicious_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (dataset_id, user_id, normal_dir, malicious_dir, normal_count, malicious_count))
            
            conn.commit()
            conn.close()
            print(f"[INFO] 数据集保存成功，dataset_id: {dataset_id}")
            return True, "数据集保存成功", dataset_id
        except Exception as e:
            print(f"[ERROR] 保存数据集失败: {str(e)}")
            return False, f"保存数据集失败: {str(e)}", None

    def get_datasets(self):
        """获取所有数据集记录
        Returns:
            list: 数据集记录列表，每个记录包含(dataset_id, normal_dir, malicious_dir, created_at)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dataset_id, normal_dir, malicious_dir, created_at
                FROM datasets
                ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"获取数据集列表时出错: {e}")
            return []

    def delete_dataset(self, dataset_id):
        """删除数据集记录
        Args:
            dataset_id: 数据集ID
        Returns:
            tuple: (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否存在
            cursor.execute('SELECT dataset_id FROM datasets WHERE dataset_id = ?', (dataset_id,))
            if not cursor.fetchone():
                return False, "数据集不存在"
            
            # 删除记录（由于设置了级联删除，相关的特征模型和机器学习模型也会被删除）
            cursor.execute('DELETE FROM datasets WHERE dataset_id = ?', (dataset_id,))
            
            conn.commit()
            conn.close()
            return True, "数据集删除成功"
        except Exception as e:
            return False, f"删除数据集失败: {str(e)}"

    def get_dataset_by_paths(self, normal_dir, malicious_dir):
        """根据路径获取数据集ID
        Args:
            normal_dir: 正常样本目录路径
            malicious_dir: 恶意样本目录路径
        Returns:
            str: 数据集ID，如果不存在则返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dataset_id FROM datasets 
                WHERE normal_dir = ? AND malicious_dir = ?
            ''', (normal_dir, malicious_dir))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"获取数据集ID时出错: {e}")
            return None

    def save_feature_model(self, dataset_id, user_id, features_dir, cv_path, tfidf_path, matrix_path, labels_path, malicious_opcode_path=None, benign_opcode_path=None):
        """保存特征模型信息到数据库"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查数据集是否存在
            cursor.execute('SELECT dataset_id FROM datasets WHERE dataset_id = ?', (dataset_id,))
            if not cursor.fetchone():
                print(f"[ERROR] 数据集 {dataset_id} 不存在")
                return False, None
            
            # 检查是否已存在该数据集的特征模型
            cursor.execute('SELECT feature_id FROM feature_models WHERE dataset_id = ?', (dataset_id,))
            if cursor.fetchone():
                print(f"[INFO] 数据集 {dataset_id} 的特征模型已存在")
                return True, None
            
            cursor.execute('''
                INSERT INTO feature_models (
                    dataset_id, user_id, features_dir, cv_path, tfidf_path, 
                    matrix_path, labels_path, malicious_opcode_path, benign_opcode_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_id, user_id, features_dir, cv_path, tfidf_path,
                matrix_path, labels_path, malicious_opcode_path, benign_opcode_path
            ))
            
            # 获取新插入的feature_id
            feature_id = cursor.lastrowid
            
            conn.commit()
            print(f"[INFO] 特征模型信息保存成功，feature_id: {feature_id}")
            return True, feature_id
        except Exception as e:
            print(f"[ERROR] 保存特征模型信息失败: {str(e)}")
            if conn:
                conn.rollback()
            return False, None
        finally:
            if conn:
                conn.close()

    def save_ml_model(self, dataset_id, user_id, model_type, version, f1_score, precision, recall, accuracy, model_path, feature_id=None, training_time=0):
        """保存机器学习模型信息到数据库"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查数据集是否存在
            cursor.execute('SELECT dataset_id FROM datasets WHERE dataset_id = ?', (dataset_id,))
            if not cursor.fetchone():
                print(f"[ERROR] 数据集 {dataset_id} 不存在")
                return False, None
            
            # 如果未提供feature_id，自动获取相同数据集ID的特征模型
            if feature_id is None:
                cursor.execute('''
                    SELECT feature_id FROM feature_models 
                    WHERE dataset_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ''', (dataset_id,))
                result = cursor.fetchone()
                if result:
                    feature_id = result[0]
                    print(f"[INFO] 自动关联特征模型，feature_id: {feature_id}")
                else:
                    print(f"[WARNING] 未找到数据集 {dataset_id} 的特征模型")
            
            # 如果提供了feature_id，检查特征模型是否存在
            elif feature_id is not None:
                cursor.execute('SELECT feature_id FROM feature_models WHERE feature_id = ?', (feature_id,))
                if not cursor.fetchone():
                    print(f"[ERROR] 特征模型 {feature_id} 不存在")
                    return False, None
            
            cursor.execute('''
                INSERT INTO ml_models (
                    dataset_id, user_id, model_type, version,
                    f1_score, precision, recall, accuracy,
                    model_path, feature_id, training_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_id, user_id, model_type, version,
                f1_score, precision, recall, accuracy,
                model_path, feature_id, training_time
            ))
            
            # 获取新插入的model_id
            model_id = cursor.lastrowid
            
            conn.commit()
            print(f"[INFO] 机器学习模型信息保存成功，model_id: {model_id}")
            return True, model_id
        except Exception as e:
            print(f"[ERROR] 保存机器学习模型信息失败: {str(e)}")
            if conn:
                conn.rollback()
            return False, None
        finally:
            if conn:
                conn.close()

    def get_latest_model(self, dataset_id, model_type):
        """获取指定数据集ID和模型类型的最新模型信息
        
        Args:
            dataset_id: 数据集ID
            model_type: 模型类型
            
        Returns:
            dict: 包含模型信息的字典，如果不存在则返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用索引查询最新模型
            cursor.execute('''
                SELECT model_id, dataset_id, user_id, model_type, version,
                       f1_score, precision, recall, accuracy, model_path,
                       feature_id, training_time, created_at
                FROM ml_models
                WHERE dataset_id = ? AND model_type = ?
                ORDER BY version DESC
                LIMIT 1
            ''', (dataset_id, model_type))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'model_id': result[0],
                    'dataset_id': result[1],
                    'user_id': result[2],
                    'model_type': result[3],
                    'version': result[4],
                    'f1_score': result[5],
                    'precision': result[6],
                    'recall': result[7],
                    'accuracy': result[8],
                    'model_path': result[9],
                    'feature_id': result[10],
                    'training_time': result[11],
                    'created_at': result[12]
                }
            return None
            
        except Exception as e:
            print(f"[ERROR] 获取最新模型信息失败: {str(e)}")
            return None

    def get_training_log_details(self, log_id):
        """获取训练日志详细信息"""
        try:
            print(f"[DEBUG] 开始获取训练日志详情，log_id: {log_id}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    id,
                    user_id,
                    start_time,
                    end_time,
                    training_time,    
                    model_name,
                    accuracy,
                    precision,
                    recall,
                    f1_score,
                    status,
                    normal_dir,
                    malicious_dir
                FROM training_logs
                WHERE id = ?
            ''', (log_id,))
            
            result = cursor.fetchone()
            print(f"[DEBUG] 查询结果: {result}")
            
            conn.close()
            
            if result:
                return {
                    'log_id': result[0],
                    'user_id': result[1],
                    'start_time': result[2],
                    'end_time': result[3],
                    'training_time': result[4],
                    'model_name': result[5],
                    'accuracy': result[6],
                    'precision': result[7],
                    'recall': result[8],
                    'f1_score': result[9],
                    'status': result[10],
                    'normal_dir': result[11] if result[11] is not None else '未知',
                    'malicious_dir': result[12] if result[12] is not None else '未知'
                }
            return None
        except Exception as e:
            print(f"[ERROR] 获取训练日志详情失败: {str(e)}")
            return None

    def get_user_models(self, user_id):
        """获取用户的所有模型列表"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        m.model_id,
                        m.model_type,
                        m.version,
                        m.accuracy,
                        m.precision,
                        m.recall,
                        m.f1_score,
                        m.model_path,
                        m.created_at,
                        d.dataset_id,
                        d.normal_dir,
                        d.malicious_dir,
                        m.user_id
                    FROM ml_models m
                    LEFT JOIN datasets d ON m.dataset_id = d.dataset_id
                    WHERE m.user_id = ?
                    ORDER BY m.created_at DESC
                """, (user_id,))
                
                models = []
                for row in cursor.fetchall():
                    model = {
                        'model_id': row[0],
                        'model_type': row[1],
                        'version': row[2],
                        'accuracy': row[3],
                        'precision': row[4],
                        'recall': row[5],
                        'f1_score': row[6],
                        'model_path': row[7],
                        'created_at': row[8],
                        'dataset_id': row[9],
                        'normal_dir': row[10],
                        'malicious_dir': row[11],
                        'user_id': row[12]
                    }
                    models.append(model)
                    
                return models
                
        except Exception as e:
            print(f"[ERROR] 获取用户模型列表失败: {str(e)}")
            return []

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def get_feature_models(self, dataset_id):
        """获取数据集的特征模型信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        feature_id,
                        features_dir,
                        cv_path,
                        tfidf_path,
                        matrix_path,
                        labels_path,
                        malicious_opcode_path,
                        benign_opcode_path
                    FROM feature_models
                    WHERE dataset_id = ?
                """, (dataset_id,))
                
                feature_models = []
                for row in cursor.fetchall():
                    feature_model = {
                        'feature_id': row[0],
                        'features_dir': row[1],
                        'cv_path': row[2],
                        'tfidf_path': row[3],
                        'matrix_path': row[4],
                        'labels_path': row[5],
                        'malicious_opcode_path': row[6],
                        'benign_opcode_path': row[7]
                    }
                    feature_models.append(feature_model)
                    
                return feature_models
                
        except Exception as e:
            print(f"[ERROR] 获取特征模型信息失败: {str(e)}")
            return []

    def delete_ml_model(self, model_id):
        """删除机器学习模型记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ml_models WHERE model_id = ?", (model_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[ERROR] 删除机器学习模型记录失败: {str(e)}")
            return False

    def delete_feature_model(self, feature_id):
        """删除特征记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM feature_models WHERE feature_id = ?", (feature_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[ERROR] 删除特征记录失败: {str(e)}")
            return False

    def get_all_datasets(self):
        """获取所有数据集"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT DISTINCT dataset_id, normal_dir, malicious_dir, normal_count, malicious_count
                FROM datasets
                ORDER BY created_at DESC
            ''')
            
            datasets = []
            for row in cursor.fetchall():
                dataset = {
                    'dataset_id': row[0],
                    'normal_dir': row[1],
                    'malicious_dir': row[2],
                    'normal_count': row[3],
                    'malicious_count': row[4]
                }
                datasets.append(dataset)
            
            return datasets
        finally:
            conn.close()

    def get_models_by_dataset(self, dataset_id, user_id=None):
        """获取指定数据集的所有模型"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if user_id is None:
                cursor.execute('''
                    SELECT m.model_id, m.model_type, m.version, m.f1_score, m.precision, 
                           m.recall, m.accuracy, m.model_path, m.created_at,
                           d.normal_dir, d.malicious_dir, m.user_id
                    FROM ml_models m
                    JOIN datasets d ON m.dataset_id = d.dataset_id
                    WHERE m.dataset_id = ?
                    ORDER BY m.version DESC
                ''', (dataset_id,))
            else:
                cursor.execute('''
                    SELECT m.model_id, m.model_type, m.version, m.f1_score, m.precision, 
                           m.recall, m.accuracy, m.model_path, m.created_at,
                           d.normal_dir, d.malicious_dir, m.user_id
                    FROM ml_models m
                    JOIN datasets d ON m.dataset_id = d.dataset_id
                    WHERE m.dataset_id = ? AND m.user_id = ?
                    ORDER BY m.version DESC
                ''', (dataset_id, user_id))
            
            models = []
            for row in cursor.fetchall():
                model = {
                    'model_id': row[0],
                    'model_type': row[1],
                    'version': row[2],
                    'f1_score': row[3],
                    'precision': row[4],
                    'recall': row[5],
                    'accuracy': row[6],
                    'model_path': row[7],
                    'created_at': row[8],
                    'normal_dir': row[9],
                    'malicious_dir': row[10],
                    'user_id': row[11]
                }
                models.append(model)
            
            return models
        finally:
            conn.close()

    def get_all_models(self):
        """获取所有模型"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.model_id, m.model_type, m.version, m.f1_score, m.precision, 
                       m.recall, m.accuracy, m.model_path, m.created_at,
                       d.normal_dir, d.malicious_dir, d.dataset_id
                FROM ml_models m
                JOIN datasets d ON m.dataset_id = d.dataset_id
                ORDER BY m.created_at DESC
            ''')
            
            models = []
            for row in cursor.fetchall():
                model = {
                    'model_id': row[0],
                    'model_type': row[1],
                    'version': row[2],
                    'f1_score': row[3],
                    'precision': row[4],
                    'recall': row[5],
                    'accuracy': row[6],
                    'model_path': row[7],
                    'created_at': row[8],
                    'normal_dir': row[9],
                    'malicious_dir': row[10],
                    'dataset_id': row[11]
                }
                models.append(model)
            
            return models
        finally:
            conn.close()

    def delete_user_data(self, user_id):
        """删除用户的所有数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除用户的所有检测日志
            cursor.execute('DELETE FROM detection_logs WHERE user_id = ?', (user_id,))
            
            # 删除用户的所有训练日志
            cursor.execute('DELETE FROM training_logs WHERE user_id = ?', (user_id,))
            
            # 删除用户的所有数据集
            cursor.execute('DELETE FROM datasets WHERE user_id = ?', (user_id,))
            
            # 删除用户的所有特征模型
            cursor.execute('DELETE FROM feature_models WHERE user_id = ?', (user_id,))
            
            # 删除用户的所有机器学习模型
            cursor.execute('DELETE FROM ml_models WHERE user_id = ?', (user_id,))
            
            # 删除用户账号
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            return True, "用户数据删除成功"
        except Exception as e:
            return False, f"删除用户数据失败: {str(e)}"

    def get_user_email(self, user_id):
        """获取用户的邮箱"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, "获取邮箱成功", result[0]
            return False, "用户不存在", None
        except Exception as e:
            return False, f"获取邮箱失败: {str(e)}", None

    def verify_user_password(self, user_id, password):
        """验证指定用户ID的密码"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            cursor.execute('SELECT id FROM users WHERE id = ? AND password = ?',
                         (user_id, hashed_password))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, "密码验证成功"
            return False, "密码错误"
        except Exception as e:
            return False, f"验证失败: {str(e)}"



    