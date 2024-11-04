import json

from info_service.utils.nacos_utils import get_config_from_nacos


class ApifyConfig:
    """
        配置类，用于从环境变量中读取配置项
    """
    config_str = get_config_from_nacos("apifyConfig.json")
    config = json.loads(config_str)

    if config:
        APIFY_API_TOKEN = config.get("APIFY_API_TOKEN")
        ACTOR_ID = config.get("ACTOR_ID")
        print("配置内容:", config)
