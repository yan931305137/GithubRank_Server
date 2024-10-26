from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from user_service.utils.logger_utils import logger

from user_service.controllers.user_controller import (
    login_user, register_user, delete_user_by_id, get_user_by_id, update_user_by_id, save_appraisal, get_appraisals
)

from user_service.utils.jwt_utils import token_required, jwt_manager

user_bp = APIRouter()


@user_bp.post('/login')
async def login(request: Request):
    """
    用户登录处理函数
    :return: 响应数据
    """
    data = await request.json()
    logger.info(f"登录请求数据: {data}")
    response = login_user(data)
    logger.info(f"登录响应数据: {response}")
    if response[1] == 200:
        logger.info("用户登录成功")
    else:
        logger.error("用户登录失败")
    return JSONResponse(content=response[0], status_code=response[1])


@user_bp.post('/register')
async def register(request: Request):
    """
    用户注册处理函数
    :return: 响应数据
    """
    data = await request.json()
    logger.info(f"注册请求数据: {data}")
    response = register_user(data)
    logger.info(f"注册响应数据: {response}")
    if response[1] == 201:
        logger.info("用户注册成功")
    else:
        logger.error("用户注册失败")
    return JSONResponse(response[0], status_code=response[1])


@user_bp.delete('/delete/{user_id}')
@token_required
async def delete_user(request: Request, user_id: int):
    """
    用户删除处理函数
    :param user_id: 用户ID
    :return: 响应数据
    """
    logger.info(f"删除用户ID: {user_id}")
    response = delete_user_by_id(user_id)
    if response[1] == 200:
        logger.info("用户删除成功")
        return JSONResponse(response[0], status_code=response[1])
    else:
        logger.error("用户删除失败")
        return JSONResponse(content=response[0], status_code=response[1])


@user_bp.get('/get/{user_id}')
@token_required
async def get_user(request: Request, user_id: int):
    """
    用户查询处理函数
    :param request:
    :param user_id: 用户ID
    :return: 响应数据
    """
    logger.info(f"查询用户ID: {user_id}")
    response = get_user_by_id(user_id)
    if response[1] == 200:
        logger.info("用户查询成功")
        return response[0]
    else:
        logger.error("用户查询失败")
        return JSONResponse(content={"error": "服务器内部错误"}, status_code=500)


@user_bp.put('/update/{user_id}')
@token_required
async def update_user(request: Request, user_id: int):  # 调整参数顺序
    """
    用户更新处理函数
    :param request:
    :param user_id: 用户ID
    :return: 响应数据
    """
    try:
        data = await request.json()
        logger.info(f"更新用户ID: {user_id}，请求数据: {data}")

        token = request.headers.get('Authorization')
        decoded_payload, error_response = jwt_manager.verify_token(token)
        if error_response:
            logger.warning(f"更新用户信息失败: 用户ID={user_id}, 错误信息: {error_response}")
            return error_response
        username = decoded_payload.get('username')

        if username != data.get('username'):
            logger.warning(
                f"用户名错误: 用户ID={user_id}, 提供的用户名={data.get('username')}, 令牌中的用户名={username}")
            return JSONResponse(content={"error": "用户名错误"}, status_code=400)

        response = update_user_by_id(user_id, data)
        if response[1] == 200:
            logger.info("用户更新成功")
        else:
            logger.error("用户更新失败")
        return JSONResponse(content=response[0], status_code=response[1])
    except Exception as e:
        logger.error(f"更新用户时发生错误，用户ID: {user_id}，错误信息: {str(e)}")
        return JSONResponse(content={"error": "服务器内部错误"}, status_code=500)


@user_bp.post('/appraise')
@token_required
async def appraise(request: Request):
    """
    用户对github用户的评价
    :return: 响应数据
    """
    # 检查Authorization头部的token
    token = request.headers.get('Authorization')
    if not token:
        logger.warning(f"请求路径: {request.url.path} - 缺少Authorization token")
        return JSONResponse(content={"error": "缺少Authorization token"}, status_code=401)

    # 验证token
    ver, err = jwt_manager.verify_token(token)
    username = ver.get('username')
    if err:
        logger.warning(f"无效的Authorization token")
        return JSONResponse(content={"error": "无效的Authorization token"}, status_code=403)
    data = await request.json()
    logger.info(f"用户评价请求已收到，数据: {username, data}")
    response = save_appraisal(username, data)
    logger.info("用户评价请求处理完毕")
    return JSONResponse(content=response[0], status_code=response[1])


@user_bp.get('/getAppraise')
async def get_appraise(request: Request):
    """
    获取用户评价
    :return: JSON响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.url.path} - 缺少github_id参数")
        return JSONResponse(content={"error": "缺少github_id参数"}, status_code=400)

    try:
        # 获取用户评价
        response_data = get_appraisals(github_id)
        logger.info(f"获取用户评价请求处理完毕，user: {github_id}")
        return response_data[0]
    except Exception as e:
        logger.error(f"获取用户评价时发生错误，user: {github_id}，错误信息: {str(e)}")
        return JSONResponse(content={"error": "服务器内部错误"}, status_code=500)
