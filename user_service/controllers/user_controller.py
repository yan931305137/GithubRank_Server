from flask import request

from user_service.services.user_service import (check_user_credentials,
                                                create_user,
                                                delete_user_by_id as service_delete_user_by_id,
                                                get_user_by_id as service_get_user_by_id,
                                                service_update_user_by_id)
from user_service.utils.cryp_utils import encrypt_password
from user_service.utils.jwt_utils import jwt_manager
from user_service.utils.logger_utils import logger


def validate_user_data(data):
    """
    验证用户数据
    :param data: 用户数据字典
    :return: 验证结果，成功返回用户名和密码，失败返回错误信息和状态码
    """
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        logger.warning(f"验证用户数据失败: 用户名或密码缺失")
        return {'error': '用户名和密码是必需的'}, 400
    logger.info(f"验证用户数据成功: 用户名={username}")
    return username, password


def login_user(data):
    """
    用户登录
    :param data: 用户登录数据
    :return: 响应数据和状态码
    """
    validation_result = validate_user_data(data)
    if isinstance(validation_result, tuple):
        username, password = validation_result
    else:
        return validation_result

    if check_user_credentials(username, password):
        logger.info(f"用户登录成功: 用户名={username}")
        token = jwt_manager.generate_token({'username': username})
        return {'message': '用户登录成功', 'token': token}, 200
    else:
        logger.warning(f"用户登录失败: 用户名或密码错误")
        return {'error': '用户名或密码错误'}, 401


def register_user(data):
    """
    用户注册
    :param data: 用户注册数据
    :return: 响应数据和状态码
    """
    validation_result = validate_user_data(data)
    if isinstance(validation_result, tuple):
        username, password = validation_result
    else:
        return validation_result

    try:
        create_user(username, encrypt_password(password))
        logger.info(f"用户注册成功: 用户名={username}")
        return {'message': '用户注册成功'}, 201
    except ValueError as e:
        logger.warning(f"用户注册失败: {str(e)}")
        return {'error': str(e)}, 400


def delete_user_by_id(user_id):
    """
    删除用户
    :param user_id: 用户ID
    :return: 响应数据和状态码
    """
    try:
        service_delete_user_by_id(user_id)
        logger.info(f"用户删除成功: 用户ID={user_id}")
        return {'message': f'用户删除成功'}, 200
    except ValueError as e:
        logger.warning(f"用户删除失败: 用户ID={user_id}, 错误信息: {str(e)}")
        return {'error': str(e)}, 404


def get_user_by_id(user_id):
    """
    获取用户信息
    :param user_id: 用户ID
    :return: 响应数据和状态码
    """
    user_data = service_get_user_by_id(user_id)
    if user_data:
        logger.info(f"查询用户成功: 用户ID={user_id}")
        return user_data, 200
    else:
        logger.warning(f"用户未找到: 用户ID={user_id}")
        return {'error': '用户未找到'}, 404


def update_user_by_id(user_id, data):
    """
    更新用户信息
    :param user_id: 用户ID
    :param data: 更新的数据
    :return: 响应数据和状态码
    """
    try:
        # 验证数据
        token = request.headers.get('Authorization')
        decoded_payload, error_response = jwt_manager.verify_token(token)
        if error_response:
            logger.warning(f"更新用户信息失败: 用户ID={user_id}, 错误信息: {error_response}")
            return error_response
        username = decoded_payload.get('username')

        if username != data.get('username'):
            logger.warning(f"用户名错误: 用户ID={user_id}, 提供的用户名={data.get('username')}, 令牌中的用户名={username}")
            return {'error': '用户名错误'}, 400

        if 'password' in data and data['password']:
            data['password'] = encrypt_password(data['password'])

        validation_result = validate_user_data(data)
        if not isinstance(validation_result, tuple):
            return validation_result

        service_update_user_by_id(user_id, data)
        logger.info(f"用户信息更新成功: 用户ID={user_id}")
        return {'message': f'用户信息更新成功'}, 200

    except ValueError as e:
        logger.warning(f"用户信息更新失败: 用户ID={user_id}, 错误信息: {str(e)}")
        return {'error': str(e)}, 400

    except Exception as e:
        logger.error(f"更新用户信息时出错: 用户ID={user_id}, 错误信息: {e}")
        return {'error': '更新用户信息失败'}, 500
