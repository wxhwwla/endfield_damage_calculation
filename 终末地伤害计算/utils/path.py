"""
跨平台路径处理、资源定位、通用IO工具等。
"""
import os

def get_project_root():
    """
    获取项目根目录，兼容打包和源码开发。
    """
    return os.path.dirname(os.path.abspath(__file__))


