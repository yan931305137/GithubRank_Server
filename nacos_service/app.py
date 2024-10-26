from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.nacos_routes import nacos_bp, client
from nacos_service.utils.logger_utils import logger
import uvicorn


# 创建并配置FastAPI应用的函数 http://127.0.0.1:8889/docs#/
def create_app():
    app = FastAPI()
    app.include_router(nacos_bp, prefix='/nacos')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8888"],  # 只允许来自主应用的请求
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("FastAPI 应用已创建并配置完成")

    return app


if __name__ == '__main__':
    app = create_app()
    try:
        client.add_naming_instance("nacos_server", "127.0.0.1", 8889)
        logger.info("服务注册成功")
    except Exception as e:
        logger.info("服务注册失败")
    # 使用配置文件中的调试模式
    uvicorn.run(app, host="127.0.0.1", port=8889)
