from flask import Blueprint, request, jsonify
from user_service.utils.logger_utils import logger

from user_service.controllers.user_controller import (
    login_user, register_user, delete_user_by_id, get_user_by_id, update_user_by_id
)

from user_service.utils.jwt_utils import token_required

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
