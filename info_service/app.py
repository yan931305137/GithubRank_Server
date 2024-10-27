from flask import Flask
from info_service.routes.info_routes import register_info_blueprint

app = Flask(__name__)

# 注册蓝图
register_info_blueprint(app)

if __name__ == '__main__':
    # 使用配置文件中的调试模式
    app.run(host="127.0.0.1", port=9002, debug=True)
