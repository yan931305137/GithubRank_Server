import json

from flask import jsonify, request, Blueprint
from nacos import NacosClient

nacos_bp = Blueprint('nacos_bp', __name__)

# Nacos 服务地址和命名空间
NACOS_SERVER_ADDRESS = "http://localhost:8848"
NAMESPACE_ID = ""
client = NacosClient(NACOS_SERVER_ADDRESS, namespace=NAMESPACE_ID)


@nacos_bp.route('/register_service', methods=['POST'])
def register_service():
    data = request.get_json()
    service_name = data.get('service_name')
    ip = data.get('ip')
    port = data.get('port')

    try:
        client.add_naming_instance(service_name, ip, port)
        return jsonify({"message": "服务注册成功"}), 200
    except Exception as e:
        return jsonify({"error": f"服务注册失败: {e}"}), 500


@nacos_bp.route('/get_config', methods=['GET'])
def get_config():
    data_id = request.args.get('data_id')
    group = request.args.get('group', 'DEFAULT_GROUP')

    if not data_id:
        return jsonify({"error": "缺少 data_id 参数"}), 400

    try:
        config = client.get_config(data_id, group)
        if config:
            return config, 200
        else:
            return jsonify({"error": "未找到配置或配置为空"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "配置内容解析错误"}), 500
    except Exception as e:
        return jsonify({"error": f"获取配置失败: {e}"}), 500
