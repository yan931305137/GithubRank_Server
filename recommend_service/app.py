from flask import Flask
from recommend_service.routes.recommend_routes import register_recommend_blueprint

app = Flask(__name__)

# 注册蓝图
register_recommend_blueprint(app)

if __name__ == '__main__':
    # 使用配置文件中的调试模式
    app.run(host="127.0.0.1", port=9003, debug=True)
