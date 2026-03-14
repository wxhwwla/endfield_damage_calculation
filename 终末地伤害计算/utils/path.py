"""
跨平台路径处理、资源定位、通用IO工具等。
"""
import os

def get_project_root():
    """
    获取项目根目录（即包含 data、model、utils 等文件夹的目录）。
    适用于源码开发和打包后的场景（如需兼容 PyInstaller 等，可在此扩展）。
    """
    # 当前文件 path.py 所在目录为 utils
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    # 项目根目录为 utils 的父目录
    return os.path.dirname(utils_dir)

def get_data_dir():
    """获取数据目录（项目根目录下的 data 文件夹）。"""
    return os.path.join(get_project_root(), "data")

def ensure_dir(file_path):
    """确保文件所在的目录存在，如果不存在则自动创建。"""
    directory = os.path.dirname(file_path)
    if directory:  # 避免空目录（如当前目录）
        os.makedirs(directory, exist_ok=True)


# ========== 常用路径常量（可直接导入使用） ==========
PROJECT_ROOT = get_project_root()
DATA_DIR = get_data_dir()

CHAR_PATH = os.path.join(DATA_DIR, "characters.json")
WEAPON_PATH = os.path.join(DATA_DIR, "weapons.json")