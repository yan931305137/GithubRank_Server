from flask import Flask
from routes.gateway_routes import gateway_bp

# 创建Flask应用实例
app = Flask(__name__)

# 从配置文件加载配置
app.config.from_object('config.config')

# 注册蓝图
app.register_blueprint(gateway_bp)

if __name__ == '__main__':
    # 运行Flask应用
    app.run(debug=app.config['DEBUG'], port=5000)
