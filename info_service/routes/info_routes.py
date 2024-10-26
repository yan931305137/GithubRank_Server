from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from info_service.controllers.info_controller import get_github_rank, get_user_info, get_user_repos_info, \
    get_user_total_info, get_user_tech_info, get_user_guess_nation_info, get_user_summary_info, get_evaluate_info
from info_service.utils.logger_utils import logger

info_bp = APIRouter()


@info_bp.get('/rank')
async def rank():
    """
    获取githubRank
    :return: 响应数据
    """
    logger.info("获取githubRank请求已收到")
    response = get_github_rank()
    logger.info("获取githubRank请求处理完毕")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/userInfo')
async def user_info(request: Request):
    """
    获取单个github用户信息
    :return: 响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(request.url.path)
        raise HTTPException(status_code=400, detail="缺少github_id参数")

    logger.info(f"获取用户信息请求已收到，github_id: {github_id}")
    response = get_user_info(github_id)
    logger.info(f"获取用户信息请求处理完毕，github_id: {github_id}")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/reposInfo')
async def repos_info(request: Request):
    """
    获取单个github用户项目信息
    :return: 响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(request.url.path)
        raise HTTPException(status_code=400, detail="缺少github_id参数")

    logger.info(f"获取用户项目信息请求已收到，github_id: {github_id}")
    response = get_user_repos_info(github_id)
    logger.info(f"获取用户项目信息请求处理完毕，github_id: {github_id}")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/total')
async def total_info(request: Request):
    """
    获取单个github用户项目stars等总数信息
    :return: 响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(request.url.path)
        raise HTTPException(status_code=400, detail="缺少github_id参数")
    user_id = request.query_params.get('github_id')
    logger.info(f"获取用户项目总数信息请求已收到，github_id: {user_id}")
    response = get_user_total_info(user_id)
    logger.info(f"获取用户项目总数信息请求处理完毕，github_id: {user_id}")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/techInfo')
async def tech_info(request: Request):
    """
    获取单个github用户技术栈信息
    :return: 响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(request.url.path)
        raise HTTPException(status_code=400, detail="缺少github_id参数")
    logger.info(f"获取用户技术栈信息请求已收到，github_id: {github_id}")
    response = get_user_tech_info(github_id)
    logger.info(f"获取用户技术栈信息请求处理完毕，github_id: {github_id}")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/guessNation')
async def guess_nation(request: Request):
    """
    获取单个github用户国家信息猜测
    :return: 响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(request.url.path)
        raise HTTPException(status_code=400, detail="缺少github_id参数")
    logger.info(f"获取用户国家信息猜测请求已收到，github_id: {github_id}")
    response = get_user_guess_nation_info(github_id)
    logger.info(f"获取用户国家信息猜测请求处理完毕，github_id: {github_id}")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/summary')
async def summary(request: Request):
    """
    获取单个github用户基于gpt的评价信息
    :return: 响应数据
    """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(request.url.path)
        raise HTTPException(status_code=400, detail="缺少github_id参数")
    logger.info(f"获取用户评价信息请求已收到，github_id: {github_id}")
    response = get_user_summary_info(github_id)
    logger.info(f"获取用户评价信息请求处理完毕，github_id: {github_id}")
    return JSONResponse(content=response[0], status_code=response[1])


@info_bp.get('/evaluate')
async def get_evaluate(request: Request):
    """
     获取用户评分
     :return: JSON响应数据
     """
    github_id = request.query_params.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.url.path} - 缺少github_id参数")
        raise HTTPException(status_code=400, detail="缺少github_id参数")

    try:
        # 获取用户评分
        response_data = get_evaluate_info(github_id)
        logger.info(f"获取用户评分请求处理完毕，user: {github_id}")
        return JSONResponse(content=response_data[0], status_code=response_data[1])
    except Exception as e:
        logger.error(f"获取用户评分时发生错误，user: {github_id}，错误信息: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
