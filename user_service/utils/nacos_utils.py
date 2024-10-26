import requests


# 获取配置示例
def get_config_from_nacos(data_id, group="DEFAULT_GROUP"):
    url = "http://localhost:8889/nacos/get_config"
    params = {"data_id": data_id, "group": group}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None


# 注册服务示例
def register_service_to_nacos(service_name, ip, port):
    url = "http://localhost:8889/nacos/register_service"
    data = {
        "service_name": service_name,
        "ip": ip,
        "port": port
    }
    response = requests.post(url, json=data)
    return response.status_code == 200
