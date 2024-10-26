from flask import Blueprint, request, jsonify

from info_service.controllers.info_controller import get_github_rank, get_user_info, get_user_repos_info, \
    get_user_total_info, get_user_tech_info, get_user_guess_nation_info, get_user_summary_info, get_evaluate_info
from info_service.utils.logger_utils import logger

info_bp = Blueprint('info_bp', __name__)


@info_bp.route('/rank', methods=['GET'])
def rank():
    """
    获取githubRank
    :return: 响应数据
    """
    logger.info("获取githubRank请求已收到")
    response = get_github_rank()
    logger.info("获取githubRank请求处理完毕")
    return jsonify(response[0]), response[1]


@info_bp.route('/userInfo', methods=['GET'])
def user_info():
    """
    获取单个github用户信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"error": "缺少github_id参数"}), 400

    logger.info(f"获取用户信息请求已收到，github_id: {github_id}")
    response = get_user_info(github_id)
    logger.info(f"获取用户信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/reposInfo', methods=['GET'])
def repos_info():
    """
    获取单个github用户项目信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"error": "缺少github_id参数"}), 400

    logger.info(f"获取用户项目信息请求已收到，github_id: {github_id}")
    response = get_user_repos_info(github_id)
    logger.info(f"获取用户项目信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/total', methods=['GET'])
def total_info():
    """
    获取单个github用户项目stars等总数信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"error": "缺少github_id参数"}), 400
    user_id = request.args.get('github_id')
    logger.info(f"获取用户项目总数信息请求已收到，github_id: {user_id}")
    response = get_user_total_info(user_id)
    logger.info(f"获取用户项目总数信息请求处理完毕，github_id: {user_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/techInfo', methods=['GET'])
def tech_info():
    """
    获取单个github用户技术栈信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"error": "缺少github_id参数"}), 400
    logger.info(f"获取用户技术栈信息请求已收到，github_id: {github_id}")
    response = get_user_tech_info(github_id)
    logger.info(f"获取用户技术栈信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/guessNation', methods=['GET'])
def guess_nation():
    """
    获取单个github用户国家信息猜测
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"error": "缺少github_id参数"}), 400
    logger.info(f"获取用户国家信息猜测请求已收到，github_id: {github_id}")
    response = get_user_guess_nation_info(github_id)
    logger.info(f"获取用户国家信息猜测请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/summary', methods=['GET'])
def summary():
    """
    获取单个github用户基于gpt的评价信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"error": "缺少github_id参数"}), 400
    logger.info(f"获取用户评价信息请求已收到，github_id: {github_id}")
    response = get_user_summary_info(github_id)
    logger.info(f"获取用户评价信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/evaluate', methods=['GET'])
def get_evaluate():
    """
     获取用户评分
     :return: JSON响应数据
     """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.path} - 缺少github_id参数")
        return jsonify({"error": "缺少github_id参数"}), 400

    try:
        # 获取用户评分
        response_data = get_evaluate_info(github_id)
        logger.info(f"获取用户评分请求处理完毕，user: {github_id}")
        return response_data
    except Exception as e:
        logger.error(f"获取用户评分时发生错误，user: {github_id}，错误信息: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500
