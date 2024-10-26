from flask import Flask
from info_service.utils.nacos_utils import register_service_to_nacos
from routes.info_routes import info_bp
from info_service.config.config import Config
from info_service.utils.logger_utils import logger


# 创建并配置 Flask 应用的函数
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(info_bp, url_prefix='/info')

    logger.info("Flask 应用已创建并配置完成")
    return app


if __name__ == '__main__':
    app = create_app()

    # 注册服务
    register_status = register_service_to_nacos("info_server", "127.0.0.1", 9002)
    logger.info(f"服务注册状态: {'成功' if register_status else '失败'}")

    # 使用配置文件中的调试模式
    app.run(debug=Config.DEBUG, port=9002)
