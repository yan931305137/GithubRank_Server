import requests
from flask import request, Response, current_app
from urllib.parse import urljoin


def forward_request(service, path):
    """
    转发请求到指定的服务
    :param service: 目标服务名称（用户服务或信息服务）
    :param path: 请求路径
    :return: 目标服务的响应
    """
    # 从配置中读取服务URL
    service_urls = {
        'user': current_app.config['USER_SERVICE_URL'],
        'info': current_app.config['INFO_SERVICE_URL']
    }

    # 根据服务名称确定目标URL
    base_url = service_urls.get(service)

    if not base_url:
        return Response(service + '服务未发现', status=404)

    url = urljoin(base_url, path)

    # 获取请求方法
    method = request.method

    # 获取请求数据
    data = request.get_data()
    headers = {key: value for key, value in request.headers if key != 'Host'}

    try:
        # 发起请求
        response = requests.request(method, url, headers=headers, data=data)
        # 返回响应
        return Response(response.content, status=response.status_code, headers=dict(response.headers))
    except requests.RequestException as e:
        return Response(f'路由转发错误: {str(e)}', status=500)
