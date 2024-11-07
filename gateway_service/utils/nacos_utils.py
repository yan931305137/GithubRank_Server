import requests

# 从Nacos获取配置的函数
def get_config_from_nacos(data_id, group="DEFAULT_GROUP"):
    url = "http://localhost:8889/get_config"
    params = {"data_id": data_id, "group": group}
    response = requests.get(url, params=params)
    # 请求成功返回JSON数据，否则返回None
    return response.json() if response.status_code == 200 else None

# 向Nacos注册服务的函数
def register_service_to_nacos(service_name, ip, port):
    url = "http://localhost:8889/register_service"
    data = {
        "service_name": service_name,
        "ip": ip,
        "port": port
    }
    response = requests.post(url, json=data)
    # 请求成功返回True
    return response.status_code == 200
