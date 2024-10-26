from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.user_routes import user_bp
from user_service.utils.logger_utils import logger
from user_service.utils.nacos_utils import register_service_to_nacos, get_config_from_nacos
import uvicorn


# 创建并配置FastAPI应用的函数 http://127.0.0.1:9001/docs#/
def create_app():
    app = FastAPI()
    app.include_router(user_bp, prefix='/user')

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
    register_status = register_service_to_nacos("user_server", "127.0.0.1", 9001)
    logger.info(f"服务注册状态: {'成功' if register_status else '失败'}")

    # 使用配置文件中的调试模式
    uvicorn.run(app, host="127.0.0.1", port=9001)
