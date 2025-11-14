# -*- coding: utf8 -*-
import warnings
import re
import os
import pickle
import hashlib
import xgboost
import subprocess
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, cross_val_predict, GridSearchCV
import joblib
from datetime import datetime
from Model.database import Database

# 定义编码列表
encodings = ['utf-8', 'gbk', 'iso-8859-1']

try:
    from rich.console import Console
    console = Console()
    print = console.print
except Exception as e:
    pass

# 获取项目根目录的绝对路径
ROOT_DIR = Path(__file__).parent.parent.parent.parent.absolute()

# 定义模型相关目录
MODELS_DIR = os.path.join(ROOT_DIR, 'models')
FEATURE_EXTRACTORS_DIR = os.path.join(MODELS_DIR, 'feature_extractors')
TRAINED_MODELS_DIR = os.path.join(MODELS_DIR)
FEATURES_DIR = os.path.join(MODELS_DIR, 'features')


# 定义文件路径
malicious_OPCODE_FILE_PATH = os.path.join(FEATURES_DIR, 'opcode', 'malicious.pkl')
benign_OPCODE_FILE_PATH = os.path.join(FEATURES_DIR, 'opcode', 'benign.pkl')
CVP = os.path.join(FEATURE_EXTRACTORS_DIR, 'countvectorizer', 'cv_model.pkl')
TFIDFP = os.path.join(FEATURE_EXTRACTORS_DIR, 'tfidf', 'tfidf_model.pkl')
X_TRAIN = os.path.join(FEATURES_DIR, 'tfidf_matrix', 'train_tfidf_matrix.pkl')
Y_LABEL = os.path.join(FEATURES_DIR, 'labels', 'train_labels.pkl')

# 定义各个模型的保存路径
DETECTION_MODEL = os.path.join(TRAINED_MODELS_DIR)


SAMPLE_DIR = os.path.join(ROOT_DIR, 'dataset', 'sample')

# 全局变量，用于控制训练是否继续
is_training = True

# 设置训练状态的函数
def set_training_state(state):
    global is_training
    is_training = state

# 获取训练状态的函数
def get_training_state():
    global is_training
    return is_training

warnings.filterwarnings("ignore")

def get_file_opcode(fp):
    php_vld_cmd = ['php', '-dvld.active=1', '-dvld.execute=0', '-dvld.dump_paths=0', '-f', fp]

    try:
        raw_out = subprocess.check_output(php_vld_cmd,
            stderr=subprocess.STDOUT)
        for encoding in encodings:
            try:
                # 尝试使用当前编码进行解码
                decoded_out = raw_out.decode(encoding)
                opcodes = re.findall(r'\*       (\b[A-Z_]+\b) ', decoded_out)
                return ' '.join(opcodes)
            except UnicodeDecodeError:
                continue
    except Exception as e:
            import traceback
            traceback.print_exc()
            return None

def extract_opcodes_for_train(ind, outp):
    g = os.walk(ind)
    result = []
    count = 0

    for path, dir_list, file_list in g:
        for fn in file_list:
            if not fn.lower().endswith('.php'): continue

            fp = os.path.join(path, fn)
            try:
                opcode_str = get_file_opcode(fp)
                if opcode_str:
                    result.append(opcode_str)
                    count += 1
                    print(count, fp, len(opcode_str))
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f'[!] {fp} error occurs!')
                pass
    
    with open(outp, 'wb') as f:
        pickle.dump(result, f)
        print(f'[^] {ind} {str(count)} php opcodes dump to {outp} !')

def extract_opcodes_for_detect(ind):
    g = os.walk(ind)
    fps = []
    opcodes = []
    count = 0

    for path, dir_list, file_list in g:
        for fn in file_list:
            if not fn.lower().endswith('.php'): continue

            fp = os.path.join(path, fn)
            try:
                opcode_str = get_file_opcode(fp)
                if opcode_str:
                    fps.append(fp)
                    opcodes.append(opcode_str)
                    count += 1
                    print(count, fn, len(opcode_str))
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f'[!] {fp} error occurs!')
                pass
    
    return fps, opcodes

def get_feature_for_train(wsod, wfod, new=False, user_id=None):
    """获取训练特征"""
    if not new:
        with open(X_TRAIN, 'rb') as f: tfidf_mat = pickle.load(f)
        with open(Y_LABEL, 'rb') as f: labels = pickle.load(f)
        return tfidf_mat, labels

    with open(wsod, 'rb') as f:
        ws_opcode_list = pickle.load(f)
        ws_count = len(ws_opcode_list)
    with open(wfod, 'rb') as f:
        wf_opcode_list = pickle.load(f)
        wf_count = len(wf_opcode_list)
    
    total = wf_count + ws_count
    labels = [1]*ws_count + [0]*wf_count
    print(labels)
    corpus = ws_opcode_list + wf_opcode_list

    covec = CountVectorizer(ngram_range=(2, 4), decode_error="ignore", max_features=10000, token_pattern=r'\b\w+\b', min_df=1, max_df=1.0)
    
    # 生成词频矩阵
    covec_mat = covec.fit_transform(corpus).toarray()

    transformer = TfidfTransformer(smooth_idf=False)
    tfidf_mat = transformer.fit_transform(covec_mat).toarray()

    # 获取数据集根目录
    dataset_root = os.path.dirname(os.path.dirname(wsod))
    features_dir = os.path.join(dataset_root, 'features')
    os.makedirs(features_dir, exist_ok=True)

    # 保存特征文件
    cv_path = os.path.join(features_dir, 'cv_model.pkl')
    tfidf_path = os.path.join(features_dir, 'tfidf_model.pkl')
    x_train_path = os.path.join(features_dir, 'train_tfidf_matrix.pkl')
    y_label_path = os.path.join(features_dir, 'train_labels.pkl')

    with open(cv_path, 'wb') as f: pickle.dump(covec, f)
    with open(tfidf_path, 'wb') as f: pickle.dump(transformer, f)
    with open(x_train_path, 'wb') as f: pickle.dump(tfidf_mat, f)
    with open(y_label_path, 'wb') as f: pickle.dump(labels, f)

    # 更新数据库中的feature_models表
    db = Database()
    
    # 使用数据集根目录计算哈希
    dataset_hash = hashlib.md5(dataset_root.encode()).hexdigest()
    print(f"[DEBUG] 使用的数据集根目录: {dataset_root}")
    print(f"[DEBUG] 计算的数据集哈希: {dataset_hash}")
    
    # 保存特征模型信息
    success, feature_id = db.save_feature_model(
        dataset_id=dataset_hash,
        user_id=user_id,
        features_dir=features_dir,
        cv_path=cv_path,
        tfidf_path=tfidf_path,
        matrix_path=x_train_path,
        labels_path=y_label_path,
        malicious_opcode_path=wsod,
        benign_opcode_path=wfod
    )
    
    if not success:
        print(f"[WARNING] 保存特征模型信息到数据库失败")

    return tfidf_mat, labels

def get_feature_for_detect(opcodes):
    """获取检测特征"""
    with open(CVP, 'rb') as f: covec = pickle.load(f)
    with open(TFIDFP, 'rb') as f: transformer = pickle.load(f)

    covec_mat = covec.transform(opcodes).toarray()
    tfidf_mat = transformer.transform(covec_mat).toarray()
    
    return tfidf_mat
    
def detect_sample(ind, model_path=DETECTION_MODEL):
    """检测样本"""
    fps, opcodes = extract_opcodes_for_detect(ind)
    x_detect = get_feature_for_detect(opcodes)
    detect_model = pickle.load(open(model_path, 'rb'))
    y_pred = detect_model.predict(x_detect)
    result = dict(zip(fps, y_pred))
    return result

def calculate_dataset_hash(malicious_dir, benign_dir):
    """计算数据集的哈希值"""
    hash_md5 = hashlib.md5()
    
    # 处理恶意样本目录
    for root, _, files in os.walk(malicious_dir):
        for file in sorted(files):
            if file.endswith('.php'):
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        hash_md5.update(chunk)
    
    # 处理正常样本目录
    for root, _, files in os.walk(benign_dir):
        for file in sorted(files):
            if file.endswith('.php'):
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        hash_md5.update(chunk)
    
    return hash_md5.hexdigest()

def get_dataset_info(malicious_dir, benign_dir):
    """获取数据集信息"""
    malicious_count = sum(1 for f in os.listdir(malicious_dir) if f.endswith('.php'))
    benign_count = sum(1 for f in os.listdir(benign_dir) if f.endswith('.php'))
    dataset_hash = calculate_dataset_hash(malicious_dir, benign_dir)
    
    return {
        'malicious_dir': malicious_dir,
        'benign_dir': benign_dir,
        'malicious_count': malicious_count,
        'benign_count': benign_count,
        'hash': dataset_hash,
        'train_start_time': datetime.now(),
        'train_duration': 0
    }
def format_duration(seconds):
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒"

def save_model_version(model, model_type, dataset_info, metrics, user_id):
    """保存模型版本"""
    # 获取数据集目录
    dataset_dir = os.path.dirname(dataset_info['malicious_dir'])
    
    # 创建models目录
    model_dir = os.path.join(dataset_dir, 'models')
    os.makedirs(model_dir, exist_ok=True)

    try:
        db = Database()
        # 查询数据库中相同数据集ID和模型类型的最新模型信息
        latest_model = db.get_latest_model(dataset_info['hash'], model_type)
        
        if latest_model:
            # 比较四个评价指标
            metrics_changed = (
                abs(latest_model['f1_score'] - metrics['f1_score']) > 0.0001 or
                abs(latest_model['precision'] - metrics['precision']) > 0.0001 or
                abs(latest_model['recall'] - metrics['recall']) > 0.0001 or
                abs(latest_model['accuracy'] - metrics['accuracy']) > 0.0001
            )
            
            if not metrics_changed:
                print("[信息] 模型评价指标与最新版本一致，不创建新版本")
                return latest_model['version'], latest_model['model_path']
            
            # 如果指标有变化，使用最新版本号+1
            version = latest_model['version'] + 1
        else:
            # 如果没有历史记录，从1开始
            version = 1

        # 生成模型文件名
        model_name = f"{model_type}_{version}.pkl"
        model_path = os.path.join(model_dir, model_name)

        # 保存模型文件
        joblib.dump(model, model_path)
    
        
        # 保存模型信息到数据库
        training_time1 = (datetime.now() - dataset_info['train_start_time']).total_seconds()
        training_time = format_duration(training_time1)
        success = db.save_ml_model(
            dataset_id=dataset_info['hash'],
            user_id=user_id,
            model_type=model_type,
            version=version,
            f1_score=metrics['f1_score'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            accuracy=metrics['accuracy'],
            model_path=model_path,
            training_time=training_time
        )
        if not success:
            print("[警告] 保存模型信息到数据库失败")
            return None, model_path

        return version, model_path

    except Exception as e:
        print(f"[错误] 保存模型信息到数据库失败: {str(e)}")
        return None, None

def train_model(x, y, model_type, dataset_info, user_id, score=False):
    """训练模型并保存版本"""
    global is_training
    if not is_training:
        print("训练已中断")
        return None, None

    # 定义参数网格
    param_grids = {
        "XGBoost": {
            'max_depth': [3, 4, 5, 6],
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2]
        },
        "SVM": {
            'C': [0.1, 1, 10],
            'loss': ['hinge', 'squared_hinge'],
            'max_iter': [1000, 2000, 3000],
            'tol': [0.1, 0.01, 0.001]
        },
        "随机森林": {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30]
        },
        "朴素贝叶斯": {
            'alpha': [0.1, 0.5, 1.0, 2.0]
        },
        "决策树": {
            'max_depth': [None, 5, 10, 15],
            'min_samples_split': [2, 5, 10]
        }
    }

    # 选择模型
    if model_type == "XGBoost":
        base_model = xgboost.XGBClassifier(eval_metric='logloss')
    elif model_type == "随机森林":
        base_model = RandomForestClassifier(oob_score=True)
    elif model_type == "决策树":
        base_model = DecisionTreeClassifier()
    elif model_type == "SVM":
        base_model = LinearSVC(max_iter=1000, tol=0.1)
    elif model_type == "朴素贝叶斯":
        base_model = MultinomialNB()
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

    # 划分数据集
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0, stratify=y)

    if not is_training:
        print("训练已中断")
        return None, None

    # 使用GridSearchCV进行超参数搜索
    print(f"开始{model_type}模型的超参数搜索...")
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grids[model_type],
        cv=5,
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(x_train, y_train)
    
    # 获取最佳模型和参数
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    
    print(f"最佳参数: {best_params}")
    print(f"最佳交叉验证分数: {grid_search.best_score_:.4f}")

    if not is_training:
        print("训练已中断")
        return None, None

    # 评估模型
    y_pred = best_model.predict(x_test)
    metrics = classification_report(y_test, y_pred, output_dict=True)

    # 提取评估指标
    metrics_summary = {
        'accuracy': metrics['accuracy'],
        'precision': metrics['weighted avg']['precision'],
        'recall': metrics['weighted avg']['recall'],
        'f1_score': metrics['weighted avg']['f1-score']
    }

    print(f"[DEBUG] 训练时使用的数据集ID: {dataset_info['hash']}")

    # 保存模型版本
    version_id, model_path = save_model_version(best_model, model_type, dataset_info, metrics_summary, user_id)

    if score:
        print('训练评估结果:')
        print(classification_report(y_test, y_pred, target_names=['Benign', 'Malicious']))
        print(f'交叉验证分数: {grid_search.best_score_:.4f}')
        y_pred_cv = cross_val_predict(best_model, x, y, cv=5)
        print('交叉验证评估结果:')
        print(classification_report(y_true=y, y_pred=y_pred_cv, target_names=['Benign', 'Malicious']))

    return best_model, metrics_summary




