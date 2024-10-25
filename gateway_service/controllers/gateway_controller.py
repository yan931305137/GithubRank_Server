import requests
from flask import request, Response, current_app, jsonify
from urllib.parse import urljoin
import logging
import time  # 用于重试机制


def forward_request(service, path, query_params):
    """
    转发请求到指定的服务
    :param service: 目标服务名称（用户服务或信息服务）
    :param path: 请求路径
    :param query_params: 查询参数
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

    # 验证请求方法
    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
    if method not in allowed_methods:
        logging.warning(f"不支持的请求方法: {method}")
        return jsonify({'error': '不支持的请求方法'}), 405

    # 获取请求数据
    data = request.get_data()
    headers = {key: value for key, value in request.headers if key != 'Host'}

    # 记录请求数据和头信息
    logging.debug(f"请求数据: {data}")
    logging.debug(f"请求头: {headers}")

    max_retries = 3  # 最大重试次数
    timeout_duration = 10  # 每次请求的超时时间

    for attempt in range(max_retries):
        try:
            # 发起请求
            logging.info(f"转发请求到 {url} 使用方法 {method} 尝试次数: {attempt + 1}")
            response = requests.request(method, url, headers=headers, data=data, params=query_params,
                                        timeout=timeout_duration)

            # 记录响应内容
            logging.debug(f"响应内容: {response.content}")

            # 返回响应
            return Response(response.content, status=response.status_code, headers=dict(response.headers))
        except requests.Timeout:
            logging.warning(f"请求超时: {url} 尝试次数: {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(1)  # 等待片刻后重试
            else:
                return jsonify({'error': '请求超时，请稍后再试'}), 504
        except requests.RequestException as e:
            logging.error(f"路由转发错误: {str(e)}")
            return jsonify({'error': f'路由转发错误: {str(e)}'}), 500
