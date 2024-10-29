import json

from nacos_service.utils.config_utils import get_nacos_config

class Config:
    """
    配置类，用于从环境变量中读取配置项
    """
    # Nacos 服务的地址和命名空间
    # 使用封装的函数获取配置
    config_str = get_nacos_config("dbConfig.json")
    config = json.loads(config_str)

    if config:
        DEBUG = config.get("DEBUG")
