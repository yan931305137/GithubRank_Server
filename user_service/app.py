from flask import Flask
from user_service.routes.user_routes import register_user_blueprint

app = Flask(__name__)

# 注册蓝图
register_user_blueprint(app)

if __name__ == '__main__':
    # 使用配置文件中的调试模式
    app.run(host="127.0.0.1", port=9001, debug=True)
