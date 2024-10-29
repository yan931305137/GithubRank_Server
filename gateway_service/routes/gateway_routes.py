from flasgger import Swagger, swag_from
from flask import jsonify, request, Blueprint

from gateway_service.controllers.gateway_controller import forward_request, forward_recommend_request

gateway_bp = Blueprint('gateway', __name__)  # 使用 Blueprint 而不是 Flask


# 在主应用中注册蓝图
def register_gateway_blueprint(app):
    app.register_blueprint(gateway_bp)
    Swagger(app)


# 对 /user/<path:path> 的请求转发到用户服务
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
    try:
        response = forward_request('user', path)
        return response
    except Exception as e:
        return jsonify(str(e)), 500


# 对 /info/<path:path> 的请求转发到信息服务
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
    try:
        response = forward_request('info', path)
        return response
    except Exception as e:
        return jsonify(str(e)), 500


# 对 /recommend/<path:path> 的请求转发到信息服务
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
    try:
        response = forward_recommend_request('recommend')
        print(response)
        return response
    except Exception as e:
        return jsonify(str(e)), 500


