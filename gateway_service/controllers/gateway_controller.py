import requests
from flask import Flask, jsonify, request
from urllib.parse import urljoin
from flask import Response

from gateway_service.utils.logger_utils import logger
from gateway_service.config.url_config import INFO_SERVICE_URL, USER_SERVICE_URL, RECOMMEND_SERVICE_URL
import time 

app = Flask(__name__)

@app.route('/forward/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def forward_request(service, path):
    """
    转发请求到指定服务
    :param service: 服务名称
    :param path: 请求路径
    """
    service_urls = {
        'user': USER_SERVICE_URL,
        'info': INFO_SERVICE_URL,
        'recommend': RECOMMEND_SERVICE_URL
    }

    base_url = service_urls.get(service)

    if not base_url:
        return jsonify({"detail": f"{service}服务未发现"}), 404

    url = urljoin(base_url, path)

    method = request.method

    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
    if method not in allowed_methods:
        logger.warning(f"不支持的请求方法: {method}")
        return jsonify({"detail": "不支持的请求方法"}), 405

    data = request.get_data()
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}

    max_retries = 3 
    timeout_duration = 600 

    for attempt in range(max_retries):
        try:
            logger.info(f"转发请求到 {url} 使用方法 {method} 尝试次数: {attempt + 1}，超时时间: {timeout_duration}秒")
            response = requests.request(method, url, headers=headers, data=data, params=request.args,
                                        timeout=timeout_duration)

            logger.debug(f"响应内容: {response}")

            if 'application/json' in response.headers.get('Content-Type', ''):
                json_content = response.json()
                return jsonify(json_content), response.status_code, dict(response.headers)
            else:
                return Response(response.content, status=response.status_code, headers=dict(response.headers))
        except requests.Timeout:
            logger.warning(f"请求超时: {url} 尝试次数: {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return jsonify({"detail": "请求超时，请稍后再试"}), 504
        except requests.RequestException as e:
            logger.error(f"路由转发错误: {str(e)}")
            return jsonify({"detail": f"路由转发错误: {str(e)}"}), 500


@app.route('/forward/<service>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def forward_recommend_request(service):
    """
    转发请求到指定服务的根路径
    :param service: 服务名称
    """
    service_urls = {
        'user': USER_SERVICE_URL,
        'info': INFO_SERVICE_URL,
        'recommend': RECOMMEND_SERVICE_URL
    }

    base_url = service_urls.get(service)

    if not base_url:
        return jsonify({"detail": f"{service}服务未发现"}), 404

    method = request.method

    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
    if method not in allowed_methods:
        logger.warning(f"不支持的请求方法: {method}")
        return jsonify({"detail": "不支持的请求方法"}), 405

    data = request.get_data()
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}

    max_retries = 3 
    timeout_duration = 600 

    for attempt in range(max_retries):
        try:
            logger.info(
                f"转发请求到 {base_url} 使用方法 {method} 尝试次数: {attempt + 1}，超时时间: {timeout_duration}秒")
            response = requests.request(method, base_url, headers=headers, data=data, params=request.args,
                                        timeout=timeout_duration)

            logger.debug(f"响应内容: {response}")

            if 'application/json' in response.headers.get('Content-Type', ''):
                json_content = response.json()
                return jsonify(json_content), response.status_code, dict(response.headers)
            else:
                return Response(response.content, status=response.status_code, headers=dict(response.headers))
        except requests.Timeout:
            logger.warning(f"请求超时: {base_url} 尝试次数: {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return jsonify({"detail": "请求超时，请稍后再试"}), 504
        except requests.RequestException as e:
            logger.error(f"路由转发错误: {str(e)}")
            return jsonify({"detail": f"路由转发错误: {str(e)}"}), 500
