from fastapi import APIRouter, Request, HTTPException
from gateway_service.controllers.gateway_controller import forward_request
from fastapi.responses import JSONResponse

gateway_bp = APIRouter()


# 对 /user/{path:path} 的请求转发到用户服务
@gateway_bp.api_route('/user/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def route_to_user_service(path: str, request: Request):
    query_params = dict(request.query_params)
    try:
        response = await forward_request('user', path, query_params, request)
        return response
    except HTTPException as e:
        return JSONResponse(content=str(e.detail), status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)


# 对 /info/{path:path} 的请求转发到信息服务
@gateway_bp.api_route('/info/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def route_to_info_service(path: str, request: Request):
    query_params = dict(request.query_params)
    try:
        response = await forward_request('info', path, query_params, request)
        return response
    except HTTPException as e:
        return JSONResponse(content=str(e.detail), status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
