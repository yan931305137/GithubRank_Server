import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from nacos import NacosClient

nacos_bp = APIRouter()

# Nacos 服务地址和命名空间
NACOS_SERVER_ADDRESS = "http://localhost:8848"
NAMESPACE_ID = ""
client = NacosClient(NACOS_SERVER_ADDRESS, namespace=NAMESPACE_ID)


@nacos_bp.post('/register_service')
async def register_service(request: Request):
    data = await request.json()
    service_name = data.get('service_name')
    ip = data.get('ip')
    port = data.get('port')

    try:
        client.add_naming_instance(service_name, ip, port)
        return JSONResponse(content={"message": "服务注册成功"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": f"服务注册失败: {e}"}, status_code=500)


@nacos_bp.get('/get_config')
async def get_config(request: Request):
    data_id = request.query_params.get('data_id')
    group = request.query_params.get('group', 'DEFAULT_GROUP')

    if not data_id:
        raise HTTPException(status_code=400, detail="缺少 data_id 参数")

    try:
        config = client.get_config(data_id, group)
        if config:
            return JSONResponse(content=config, status_code=200)
        else:
            return JSONResponse(content={"error": "未找到配置或配置为空"}, status_code=404)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "配置内容解析错误"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": f"获取配置失败: {e}"}, status_code=500)
