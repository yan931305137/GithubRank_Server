import json

from info_service.utils.nacos_utils import get_config_from_nacos


class Config:
    """
    配置类，用于从环境变量中读取配置项
    """
    # 从Nacos获取配置字符串
    config_str = get_config_from_nacos("dbConfig.json")
    # 将配置字符串转换为字典
    config = json.loads(config_str)

    # 如果配置字典不为空，则从中获取数据库配置
    if config:
        DB_HOST = config.get("DB_HOST")
        DB_USER = config.get("DB_USER")
        DB_PASSWORD = config.get("DB_PASSWORD")
        DB_NAME = config.get("DB_NAME")
        DB_PORT = config.get("DB_PORT")
        DB_CHARSET = config.get("DB_CHARSET")

        # 打印配置内容
        print("配置内容:", config)
