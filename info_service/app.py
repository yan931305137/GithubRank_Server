from flask import Flask
from info_service.routes.info_routes import register_info_blueprint
import os

app = Flask(__name__)

# 需要代理的要设置环境变量
# os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
# os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'

# 注册蓝图
register_info_blueprint(app)

if __name__ == '__main__':
    # 使用配置文件中的调试模式
    app.run(host="127.0.0.1", port=9002, debug=True)
