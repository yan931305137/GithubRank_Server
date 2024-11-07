from flasgger import Swagger, swag_from
from flask import jsonify, request, Blueprint

from gateway_service.controllers.gateway_controller import forward_request, forward_recommend_request

# 定义网关服务的蓝图
gateway_bp = Blueprint('gateway', __name__)

# 注册网关蓝图到应用
def register_gateway_blueprint(app):
    app.register_blueprint(gateway_bp)
    Swagger(app)

# 定义路由到用户服务的函数
@gateway_bp.route('/user/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['网关服务'],
    'parameters': [
        {
            'name': 'path',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': '用户服务的路径'
        },
        {
            'name': 'query_params',
            'in': 'query',
            'required': False,
            'type': 'object',
            'description': '查询参数'
        }
    ],
    'responses': {
        200: {
            'description': '请求成功'
        },
        500: {
            'description': '服务器内部错误'
        }
    }
})
def route_to_user_service(path):
    """
    转发请求到用户服务
    :param path: 用户服务的路径
    """
    try:
        # 调用forward_request函数转发请求到用户服务
        response = forward_request('user', path)
        return response
    except Exception as e:
        # 如果发生异常，返回错误信息和状态码500
        return jsonify(str(e)), 500

# 定义路由到信息服务的函数
@gateway_bp.route('/info/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['网关服务'],
    'parameters': [
        {
            'name': 'path',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': '信息服务的路径'
        },
        {
            'name': 'query_params',
            'in': 'query',
            'required': False,
            'type': 'object',
            'description': '查询参数'
        }
    ],
    'responses': {
        200: {
            'description': '请求成功'
        },
        500: {
            'description': '服务器内部错误'
        }
    }
})
def route_to_info_service(path):
    """
    转发请求到信息服务
    :param path: 信息服务的路径
    """
    try:
        # 调用forward_request函数转发请求到信息服务
        response = forward_request('info', path)
        return response
    except Exception as e:
        # 如果发生异常，返回错误信息和状态码500
        return jsonify(str(e)), 500

# 定义路由到推荐服务的函数
@gateway_bp.route('/recommend', methods=['GET', 'POST', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['网关服务'],
    'parameters': [
        {
            'name': 'path',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': '信息服务的路径'
        },
        {
            'name': 'query_params',
            'in': 'query',
            'required': False,
            'type': 'object',
            'description': '查询参数'
        }
    ],
    'responses': {
        200: {
            'description': '请求成功'
        },
        500: {
            'description': '服务器内部错误'
        }
    }
})
def route_to_recommend_service():
    """
    转发请求到推荐服务
    """
    try:
        # 调用forward_recommend_request函数转发请求到推荐服务
        response = forward_recommend_request('recommend')
        print(response)  # 打印响应内容
        return response
    except Exception as e:
        # 如果发生异常，返回错误信息和状态码500
        return jsonify(str(e)), 500
