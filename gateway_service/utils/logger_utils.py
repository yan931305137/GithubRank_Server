import logging
import os
from datetime import datetime

def setup_logger():
    # 创建日志目录，如果不存在
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)

    # 根据当前日期生成日志文件名
    log_filename = datetime.now().strftime("%Y-%m-%d.log")
    log_filepath = os.path.join(log_dir, log_filename)

    # 配置日志设置
    logging.basicConfig(level=logging.INFO,  # 设置日志级别为INFO
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
                        handlers=[
                            logging.FileHandler(log_filepath),  # 将日志写入文件
                            logging.StreamHandler()  # 同时输出到控制台
                        ])
    return logging.getLogger(__name__)

# 初始化日志器
logger = setup_logger()
