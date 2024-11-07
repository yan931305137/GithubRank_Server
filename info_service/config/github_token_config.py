import json

from info_service.utils.nacos_utils import get_config_from_nacos


class Config:
    """
        配置类，用于从环境变量中读取配置项
    """
    config_str = get_config_from_nacos("githubToken.json")
    config = json.loads(config_str)

    if config:
        token = config.get("token")
        print("配置内容:", config)
