from flask import Blueprint, current_app, Response
from gateway_service.controllers.gateway_controller import forward_request

# 创建一个蓝图对象，用于注册路由
gateway_bp = Blueprint('gateway_bp', __name__)


# 对 /user/<path:path> 的请求转发到用户服务
@gateway_bp.route('/user/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def route_to_user_service(path):
    """
    路由到用户服务的处理函数
    :param path: 请求路径
    :return: 用户服务的响应
    """
    try:
        # 转发请求
        response = forward_request('user', path)
        return response
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(f"user路由到用户服务时出错: {str(e)}")
        return Response('user内部服务器错误', status=500)


# 对 /info/<path:path> 的请求转发到信息服务
@gateway_bp.route('/info/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def route_to_info_service(path):
    """
    路由到信息服务的处理函数
    :param path: 请求路径
    :return: 用户服务的响应
    """
    try:
        # 转发请求
        response = forward_request('info', path)
        return response
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(f"info路由到信息服务时出错: {str(e)}")
        return Response('info内部服务器错误', status=500)
