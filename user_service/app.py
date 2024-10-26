from flask import Flask
from routes.user_routes import user_bp
from user_service.config.config import Config
from user_service.utils.logger_utils import logger
from user_service.utils.nacos_utils import register_service_to_nacos


# 创建并配置Flask应用的函数
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(user_bp, url_prefix='/user')

    # 设置日志
    logger.info("Flask 应用已创建并配置完成")

    return app


if __name__ == '__main__':
    register_status = register_service_to_nacos("info_server", "127.0.0.1", 9001)
    logger.info("服务注册状态:", "成功" if register_status else "失败")
    app = create_app()
    # 使用配置文件中的调试模式
    app.run(debug=Config.DEBUG, port=9001)
