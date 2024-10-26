from nacos import NacosClient
import json


def get_nacos_config(data_id, group, service_name, ip, port, nacos_server="http://localhost:8848", namespace=""):
    """
    从 Nacos 获取 JSON 格式的配置，并返回指定的配置内容。

    :param data_id: 配置的 data_id
    :param group: 配置的 group
    :param service_name: 注册的服务名称
    :param ip: 服务实例的 IP 地址
    :param port: 服务实例的端口
    :param nacos_server: Nacos 服务地址
    :param namespace: Nacos 命名空间
    :return: 解析后的 JSON 配置字典，或 None 如果获取失败
    """
    # 初始化 Nacos 客户端
    client = NacosClient(nacos_server, namespace=namespace)

    # 注册服务实例
    client.add_naming_instance(service_name, ip, port)

    try:
        # 从 Nacos 获取配置
        config = client.get_config(data_id, group)
        if config:
            # 解析 JSON 配置
            config_dict = json.loads(config)
            return config_dict
        else:
            print("未找到配置或配置为空")
            return None
    except json.JSONDecodeError:
        print("配置内容解析错误，检查配置格式是否为有效的 JSON")
        return None
    except Exception as e:
        print(f"获取配置失败: {e}")
        return None

