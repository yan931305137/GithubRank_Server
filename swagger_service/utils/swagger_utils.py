import requests
from flask import current_app as app

# 获取Swagger文档
def get_swagger_spec(service_url):
    try:
        response = requests.get(service_url)
        response.raise_for_status()  # 添加错误处理
        return response.json()
    except requests.RequestException as e:
        app.logger.error(f"获取Swagger文档失败: {e}")
        return {}

# 合并Swagger文档
def merge_swagger_specs(service_specs):
    combined_spec = {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "Combined API"
        },
        "paths": {}
    }

    for service_name, service_spec in service_specs.items():
        if not service_spec:
            continue
        # 使用服务名称作为模块名
        for path, path_spec in service_spec.get("paths", {}).items():
            combined_path = f"{path}"
            combined_spec["paths"][combined_path] = path_spec

    return combined_spec

