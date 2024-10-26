from info_service.utils.nacos_utils import get_config_from_nacos


class Config:
    """
    配置类，用于从环境变量中读取配置项
    """
    config = get_config_from_nacos("dbConfig.json")

    if config:
        DEBUG = config.get("DEBUG")
        DB_HOST = config.get("DB_HOST")
        DB_USER = config.get("DB_USER")
        DB_PASSWORD = config.get("DB_PASSWORD")
        DB_NAME = config.get("DB_NAME")
        DB_PORT = config.get("DB_PORT")
        DB_CHARSET = config.get("DB_CHARSET")

        print("配置内容:", config)
