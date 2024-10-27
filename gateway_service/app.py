from flask import Flask
from gateway_service.routes.gateway_routes import register_gateway_blueprint

app = Flask(__name__)

# 注册蓝图
register_gateway_blueprint(app)

if __name__ == '__main__':
    # 使用配置文件中的调试模式
    app.run(host="127.0.0.1", port=9000, debug=True)
