from flask import Flask

from routes.nacos_routes import nacos_bp, client
from nacos_service.config.config import Config
from nacos_service.utils.logger_utils import logger


# 创建并配置Flask应用的函数
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(nacos_bp)

    # 设置日志
    logger.info("Flask 应用已创建并配置完成")

    return app


if __name__ == '__main__':
    app = create_app()
    try:
        client.add_naming_instance("nacos_server", "127.0.0.1", 8889)
        logger.info("服务注册成功")
    except Exception as e:
        logger.info("服务注册失败")
    # 使用配置文件中的调试模式
    app.run(debug=Config.DEBUG, port=8889)
