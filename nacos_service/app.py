from flask import Flask
from routes.nacos_routes import register_nacos_blueprint, client
from nacos_service.utils.logger_utils import logger

app = Flask(__name__)

# 注册 Nacos 蓝图
register_nacos_blueprint(app)


def register_service():
    """尝试注册服务到 Nacos"""
    service_name = "nacos_server"
    ip = "127.0.0.1"
    port = 8889

    try:
        client.add_naming_instance(service_name, ip, port)
        logger.info("服务注册成功")
    except Exception as e:
        logger.error(f"服务注册失败: {str(e)}")


if __name__ == '__main__':
    register_service()  # 在应用启动时注册服务
    # 使用配置文件中的调试模式
    app.run(host="127.0.0.1", port=8889, debug=True)
