from flask import Flask
from routes.user_routes import user_bp
from user_service.config.config import Config
from user_service.utils.logger_utils import logger


# 创建并配置Flask应用的函数
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(user_bp, url_prefix='/user')

    # 设置日志
    logger.info("Flask 应用已创建并配置完成")

    return app


if __name__ == '__main__':
    app = create_app()
    # 使用配置文件中的调试模式
    app.run(debug=Config.DEBUG, port=9001)
