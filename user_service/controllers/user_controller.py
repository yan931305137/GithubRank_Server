from user_service.services.user_service import (check_user_credentials,
                                                create_user,
                                                delete_user_by_id as service_delete_user_by_id,
                                                get_user_by_id as service_get_user_by_id,
                                                service_update_user_by_id, get_user_appraisals, save_user_appraisal)
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
        if service_delete_user_by_id(user_id):
            logger.info(f"用户删除成功: 用户ID={user_id}")
            return {'message': f'用户删除成功'}, 200
        else:
            logger.warning(f"用户删除失败: 用户ID={user_id}")
            return {'error':f'用户删除失败'}, 400
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


def save_appraisal(username, data):
    """
    保存评估数据。
    :param username: 用户名
    :param data: 包含 'github_id'、'message' 和 'point' 的评估数据字典
    """
    try:
        logger.info(f"开始保存评估数据，用户名: {username}, 数据: {data}")

        # 获取数据中的必要字段
        github_id = data.get('github_id')
        message = data.get('message')
        point = data.get('point')

        # 检查必要字段是否存在
        if not all([github_id, message, point]):
            logger.error("评估数据缺失必要字段")
            return {'error': '评估数据缺失必要字段'}, 400

        # 调用保存函数
        result = save_user_appraisal(username, github_id, message, point)

        if result:
            logger.info("评估数据保存成功")
            return {'message': '评估数据保存成功'}, 201
        else:
            logger.error("评估数据保存失败，可能是用户不存在")
            return {'error': '评估数据保存失败'}, 400

    except Exception as e:
        logger.error(f"保存评估数据失败: {e}")
        return {'error': '服务器内部错误'}, 500


def get_appraisals(github_id):
    """
    获取用户的所有评估。
    :param github_id:
    :param info_id: 用户ID
    """
    try:
        logger.info(f"开始获取用户评估，用户ID: {github_id}")
        appraisals = get_user_appraisals(github_id)
        logger.info(f"成功获取用户评估: {appraisals}")
        return appraisals,200
    except Exception as e:
        logger.error(f"获取用户评估失败，用户ID: {github_id}, 错误: {e}")
        return {'error': '获取用户评估失败'}, 500
