from flask import Blueprint, request, jsonify

from user_service.utils.logger_utils import logger

from user_service.controllers.user_controller import (
    login_user, register_user, delete_user_by_id, get_user_by_id, update_user_by_id, save_appraisal, get_appraisals
)

from user_service.utils.jwt_utils import token_required, jwt_manager

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录处理函数
    :return: 响应数据
    """
    data = request.get_json()
    logger.info(f"登录请求数据: {data}")
    response = login_user(data)
    logger.info(f"登录响应数据: {response}")
    if response[1] == 200:
        logger.info("用户登录成功")
    else:
        logger.error("用户登录失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册处理函数
    :return: 响应数据
    """
    data = request.get_json()
    logger.info(f"注册请求数据: {data}")
    response = register_user(data)
    logger.info(f"注册响应数据: {response}")
    if response[1] == 201:
        logger.info("用户注册成功")
    else:
        logger.error("用户注册失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """
    用户删除处理函数
    :param user_id: 用户ID
    :return: 响应数据
    """
    logger.info(f"删除用户ID: {user_id}")
    response = delete_user_by_id(user_id)
    if response[1] == 200:
        logger.info("用户删除成功")
    else:
        logger.error("用户删除失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/get/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    用户查询处理函数
    :param user_id: 用户ID
    :return: 响应数据
    """
    logger.info(f"查询用户ID: {user_id}")
    response = get_user_by_id(user_id)
    if response[1] == 200:
        logger.info("用户查询成功")
    else:
        logger.error("用户查询失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/update/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """
    用户更新处理函数
    :param user_id: 用户ID
    :return: 响应数据
    """
    data = request.get_json()
    logger.info(f"更新用户ID: {user_id}，请求数据: {data}")
    response = update_user_by_id(user_id, data)
    if response[1] == 200:
        logger.info("用户更新成功")
    else:
        logger.error("用户更新失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/appraise', methods=['POST'])
@token_required
def appraise():
    """
    用户对github用户的评价
    :return: 响应数据
    """
    # 检查Authorization头部的token
    token = request.headers.get('Authorization')
    if not token:
        logger.warning(f"请求路径: {request.path} - 缺少Authorization token")
        return jsonify({"error": "缺少Authorization token"}), 401

    # 验证token
    ver, err = jwt_manager.verify_token(token)
    username = ver.get('username')
    print(username)
    if err:
        logger.warning(f"无效的Authorization token")
        return jsonify({"error": "无效的Authorization token"}), 403
    data = request.json
    logger.info(f"用户评价请求已收到，数据: {username, data}")
    response = save_appraisal(username, data)
    logger.info("用户评价请求处理完毕")
    return jsonify(response[0]), response[1]


@user_bp.route('/getAppraise', methods=['GET'])
def get_appraise():
    """
    获取用户评价
    :return: JSON响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.path} - 缺少github_id参数")
        return jsonify({"error": "缺少github_id参数"}), 400

    try:
        # 获取用户评价
        response_data = get_appraisals(github_id)
        logger.info(f"获取用户评价请求处理完毕，user: {github_id}")
        return response_data
    except Exception as e:
        logger.error(f"获取用户评价时发生错误，user: {github_id}，错误信息: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500
