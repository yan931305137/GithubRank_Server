import logging
import os
from datetime import datetime


def setup_logger():
    # 确保日志目录存在
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)

    # 动态生成日志文件名
    log_filename = datetime.now().strftime("%Y-%m-%d.log")
    log_filepath = os.path.join(log_dir, log_filename)

    # 配置日志
    logging.basicConfig(level=logging.INFO,  # 设置日志级别
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
                        handlers=[
                            logging.FileHandler(log_filepath),  # 将日志输出到文件
                            logging.StreamHandler()  # 同时输出到控制台
                        ])
    return logging.getLogger(__name__)


logger = setup_logger()
