import json
from flask import Blueprint, jsonify, request
from nacos import NacosClient
from nacos_service.utils.logger_utils import logger
from flasgger import Swagger, swag_from

# 定义蓝图
nacos_bp = Blueprint('nacos', __name__)


# 在主应用中注册蓝图
def register_nacos_blueprint(app):
    app.register_blueprint(nacos_bp, url_prefix='/nacos')
    Swagger(app)  # 初始化 Swagger


# Nacos 服务地址和命名空间
NACOS_SERVER_ADDRESS = "http://localhost:8848"
NAMESPACE_ID = ""
client = NacosClient(NACOS_SERVER_ADDRESS, namespace=NAMESPACE_ID)


@nacos_bp.route('/register_service', methods=['POST'])
@swag_from({
    'tags': ['Nacos'],
    'parameters': [
        {
            'name': 'service_name',
            'type': 'string',
            'required': True,
            'description': '服务名称'
        },
        {
            'name': 'ip',
            'type': 'string',
            'required': True,
            'description': '服务 IP 地址'
        },
        {
            'name': 'port',
            'type': 'integer',
            'required': True,
            'description': '服务端口'
        }
    ],
    'responses': {
        200: {
            'description': '服务注册成功'
        },
        400: {
            'description': '缺少必要的参数'
        },
        500: {
            'description': '服务注册失败'
        }
    }
})
def register_service():
    """注册服务"""
    data = request.json
    service_name = data.get('service_name')
    ip = data.get('ip')
    port = data.get('port')

    if not service_name or not ip or not port:
        return jsonify({"error": "缺少必要的参数: service_name, ip, port"}), 400

    try:
        client.add_naming_instance(service_name, ip, port)
        return jsonify({"message": "服务注册成功"}), 200
    except Exception as e:
        logger.error(f"服务注册失败: {e}")
        return jsonify({"error": f"服务注册失败: {str(e)}"}), 500


@nacos_bp.route('/get_config', methods=['GET'])
@swag_from({
    'tags': ['Nacos'],
    'parameters': [
        {
            'name': 'data_id',
            'type': 'string',
            'required': True,
            'description': '配置的 data_id'
        },
        {
            'name': 'group',
            'type': 'string',
            'required': False,
            'default': 'DEFAULT_GROUP',
            'description': '配置组名'
        }
    ],
    'responses': {
        200: {
            'description': '返回配置内容'
        },
        400: {
            'description': '缺少 data_id 参数'
        },
        404: {
            'description': '未找到配置或配置为空'
        },
        500: {
            'description': '获取配置失败'
        }
    }
})
def get_config():
    """获取配置"""
    data_id = request.args.get('data_id')
    group = request.args.get('group', 'DEFAULT_GROUP')

    if not data_id:
        return jsonify({"error": "缺少 data_id 参数"}), 400

    try:
        config = client.get_config(data_id, group)
        if config:
            return jsonify(config), 200
        else:
            return jsonify({"error": "未找到配置或配置为空"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "配置内容解析错误"}), 500
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({"error": f"获取配置失败: {str(e)}"}), 500
