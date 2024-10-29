from flasgger import Swagger, swag_from

from flask import jsonify, request, Blueprint

from recommend_service.utils.logger_utils import logger

from recommend_service.controllers.recommend_controller import get_weekly_recommend

# 定义蓝图
recommend_bp = Blueprint('recommend', __name__)


# 在主应用中注册蓝图
def register_recommend_blueprint(app):
    app.register_blueprint(recommend_bp, url_prefix='/recommend')
    Swagger(app)


@recommend_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['推荐服务'],
})
def recommend():
    weekly = request.args.get('since')
    if not weekly:
        logger.error(f"请求路径: {request.path} - 缺少weekly参数")
        return jsonify({"detail": "缺少weekly参数"}), 400
    try:
        # 获取每周推荐评分
        response_data = get_weekly_recommend()
        return jsonify(response_data[0]), response_data[1]
    except Exception as e:
        logger.error(f"处理推荐请求时出错: {e}")
        return jsonify({"detail": "服务器内部错误"}), 500
