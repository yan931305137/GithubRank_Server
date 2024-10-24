from flask import Blueprint, request, jsonify

from info_service.controllers.info_controller import get_github_rank, get_user_info, save_appraisal, get_appraisals
from info_service.utils.logger_utils import logger

from info_service.utils.jwt_utils import token_required

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
def userInfo():
    """
    获取单个github用户信息
    :return: 响应数据
    """
    user_id = request.args.get('github_id')
    logger.info(f"获取用户信息请求已收到，github_id: {user_id}")
    response = get_user_info(user_id)
    logger.info(f"获取用户信息请求处理完毕，github_id: {user_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/appraise', methods=['POST'])
@token_required
def appraise():
    """
    用户对github用户的评价
    :return: 响应数据
    """
    data = request.json
    logger.info(f"用户评价请求已收到，数据: {data}")
    response = save_appraisal(data)
    logger.info("用户评价请求处理完毕")
    return jsonify(response[0]), response[1]


@info_bp.route('/getAppraise', methods=['GET'])
def getAppraise():
    """
    获取用户评价
    :return: 响应数据
    """
    user_id = request.args.get('user')
    logger.info(f"获取用户评价请求已收到，user: {user_id}")
    response = get_appraisals(user_id)
    logger.info(f"获取用户评价请求处理完毕，user: {user_id}")
    return jsonify(response[0]), response[1]
