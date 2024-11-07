import json

from info_service.utils.nacos_utils import get_config_from_nacos


class CohereConfig:
    """
        配置类，用于从环境变量中读取配置项
    """
    # 从Nacos中获取配置字符串
    config_str = get_config_from_nacos("cohereConfig.json")
    # 将配置字符串转换为字典
    config = json.loads(config_str)

    # 如果配置字典不为空，则从中获取COHEREKEY
    if config:
        COHEREKEY = config.get("COHEREKEY")
        # 打印配置内容
        print("配置内容:", config)
