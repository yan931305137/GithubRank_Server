from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from info_service.routes.info_routes import info_bp
from info_service.utils.logger_utils import logger
from info_service.utils.nacos_utils import register_service_to_nacos
import uvicorn


# 创建并配置 FastAPI 应用的函数 http://127.0.0.1:9002/docs#/
def create_app():
    app = FastAPI()
    app.include_router(info_bp, prefix='/info')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8888"],  # 只允许来自主应用的请求
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("FastAPI 应用已创建并配置完成")
    return app


app = create_app()

if __name__ == '__main__':
    register_status = register_service_to_nacos("info_server", "127.0.0.1", 9002)
    logger.info(f"服务注册状态: {'成功' if register_status else '失败'}")

    # 使用配置文件中的调试模式
    uvicorn.run(app, host="127.0.0.1", port=9002)
