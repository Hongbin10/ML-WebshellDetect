# Webshell Detection System

## 📖 Project Overview

WebshellDEtect is a machine learning-based Webshell detection system designed to help security researchers and administrators discover malicious PHP scripts on servers. The system adopts an MVC architecture, combining PHP Opcode analysis with various machine learning algorithms (such as XGBoost, Random Forest, SVM, etc.) to provide efficient and accurate detection capabilities.

The system is equipped with a graphical user interface (GUI) based on PyQt5, supporting functions such as user management, model training, file scanning, log viewing, etc., with intuitive and convenient operations.

## ✨ Key Features

- **Multi-model Support**: Built-in support for multiple machine learning algorithms, including:
    - XGBoost
    - Random Forest
    - Decision Tree
    - Linear SVM (Linear Support Vector Machine)
    - Naive Bayes
- **In-depth Opcode Analysis**: Utilizes the PHP VLD extension to extract the Opcode sequence of scripts, vectorizes features based on TF-IDF, performs detection at the in-depth code logic layer, and effectively combats code obfuscation.
- **Real-time Detection and Scanning**: Supports single-file and directory scanning, enabling quick identification of potential Webshell files.
- **Custom Training**: Users can upload malicious and benign samples to retrain the model to adapt to new threat environments.
- **User Management System**: Built-in SQLite database, supporting user registration, login, and personal file management.
- **Detection Reports and Logs**: Automatically generates detection reports and provides detailed log recording functions.

## 🛠️ Requirements

### Basic Environment
- **Operating System**: macOS / Linux / Windows
- **Python**: 3.8+
- **PHP**: 7.x/8.x (VLD extension must be installed)

### PHP VLD Extension Installation
The detection core relies on PHP's VLD (Vulcan Logic Dumper) extension to extract Opcode. Please ensure that your environment has been correctly installed and configured.

**Linux/macOS:**
```bash
pecl install vld
# And add in php.ini: extension=vld.so
```

### Python Dependencies
The project depends on the following Python libraries, please install them using pip:

```bash
pip install PyQt5 scikit-learn xgboost rich joblib
```

## 🚀 Installation & Usage

1. **Clone the Project**
    ```bash
    git clone <repository_url>
    cd WebshellDEtect
    ```

2. **Install Dependencies**
    Ensure that you have installed all the above Python libraries and the PHP VLD environment.

3. **Run the System**
    Execute in the project root directory:
    ```bash
    python main.py
    ```

4. **System Login**
    - A login interface will be displayed after startup.
    - If it's your first use, please register according to the prompts or use the default credentials (if any).

## 📂 Project Structure

```
WebshellDEtect/
├── Controller/         # Control layer: handles business logic threads (detection, training, processing)
├── Model/              # Model layer: contains core algorithms, database interaction, Opcode extraction
│   ├── detect.py       # Detection logic
│   ├── train.py        # Model training logic
│   └── database.py     # Database operations
├── View/               # View layer: PyQt5 GUI interface code
│   ├── main_window.py  # Main window
│   └── ...             # Various functional pages
├── Utils/