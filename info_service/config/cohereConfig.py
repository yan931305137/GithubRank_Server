from info_service.utils.nacos_utils import get_config_from_nacos


class Config:
    """
        配置类，用于从环境变量中读取配置项
    """
    config = get_config_from_nacos("cohereConfig.json")

    if config:
        COHEREKEY = config.get("COHEREKEY")
        print("配置内容:", COHEREKEY)
