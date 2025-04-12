import base64
import os
import re
from typing import Optional, Union
import configparser

def path_to_base64(image_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    将图片文件路径转换为 base64 编码字符串
    
    参数:
        image_path (str): 图片文件的路径
        encoding (str): 编码方式，默认为 'utf-8'
        
    返回:
        Optional[str]: 成功时返回 base64 编码的字符串，失败时返回 None
    """
    try:
        if not os.path.exists(image_path):
            print(f"错误: 文件 '{image_path}' 不存在")
            return None
            
        with open(image_path, 'rb') as image_file:
            # 读取图片文件并进行 base64 编码
            encoded_string = base64.b64encode(image_file.read())
            # 将二进制编码转换为字符串
            return encoded_string.decode(encoding)
    except Exception as e:
        print(f"转换图片到 base64 时出错: {str(e)}")
        return None

def process_image_path_or_url(path_or_url: str, encoding: str = 'utf-8') -> str:
    """
    处理图片路径或URL
    
    参数:
        path_or_url (str): 图片的本地路径或HTTP URL
        encoding (str): 编码方式，默认为 'utf-8'
        
    返回:
        str: 如果输入是URL则直接返回，如果是本地路径则返回base64编码
    """
    # 使用正则表达式检查是否为HTTP/HTTPS URL
    if re.match(r'^https?://', path_or_url):
        return path_or_url
    else:
        # 假设是本地路径，尝试转换为base64
        base64_str = path_to_base64(path_or_url, encoding)
        if base64_str:
            return base64_str
        return path_or_url  # 如果转换失败，返回原始路径
    

def get_comfyonline_config():
    curr_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 获取上级目录
    comfyonline_config_path = os.path.join(curr_dir, "config.ini")
    config = configparser.ConfigParser()
    config.read(comfyonline_config_path)
    return config

def get_comfyonline_api_key():
    config = get_comfyonline_config()
    config_api_key = config.get("comfyonline").get("api_key")
    env_api_token = os.getenv("COMFYONLINE_TOKEN")
    if not env_api_token:
        api_token = config_api_key
    else:
        api_token = env_api_token
    return api_token

