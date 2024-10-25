from flask import Blueprint, current_app, Response, request
from gateway_service.controllers.gateway_controller import forward_request

# 创建一个蓝图对象，用于注册路由
gateway_bp = Blueprint('gateway_bp', __name__)


def handle_request(service_name, path):
    """
    通用的请求处理函数
    :param service_name: 服务名称
    :param path: 请求路径
    :return: 服务的响应
    """
    try:
        # 获取查询参数
        query_params = request.args.to_dict()
        
        # 转发请求，传递查询参数
        response = forward_request(service_name, path, query_params)
        return response
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(f"{service_name}路由到服务时出错: {str(e)} - 方法: {request.method}, 路径: {path}")
        return Response(f'{service_name}内部服务器错误', status=500)


# 对 /user/<path:path> 的请求转发到用户服务
@gateway_bp.route('/user/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def route_to_user_service(path):
    return handle_request('user', path)


# 对 /info/<path:path> 的请求转发到信息服务
@gateway_bp.route('/info/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def route_to_info_service(path):
    return handle_request('info', path)
