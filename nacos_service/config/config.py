from nacos_service.utils.config_utils import get_nacos_config
class Config:
    """
    配置类，用于从环境变量中读取配置项
    """
    # Nacos 服务的地址和命名空间
    # 使用封装的函数获取配置
    data_id = "dbConfig.json"
    group = "DEFAULT_GROUP"
    service_name = "nacos_server"
    ip = "127.0.0.1"
    port = 8889
    config = get_nacos_config(data_id, group, service_name, ip, port)
    if config:
        DEBUG = config.get("DEBUG")