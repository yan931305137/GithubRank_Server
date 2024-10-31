from flasgger import Swagger, swag_from

from flask import jsonify, request, Blueprint

from recommend_service.utils.logger_utils import logger

from recommend_service.controllers.recommend_controller import get_since_recommend

# 定义蓝图
recommend_bp = Blueprint('recommend', __name__)


# 在主应用中注册蓝图
def register_recommend_blueprint(app):
    app.register_blueprint(recommend_bp, url_prefix='/recommend')
    Swagger(app)


@recommend_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['推荐服务'],
    'parameters': [
        {
            'name': 'since',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': '推荐周期参数，可以是daily, weekly, 或 monthly'
        }
    ],
    'responses': {
        200: {
            'description': '成功返回推荐数据',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'username': {'type': 'string'},
                        'avatar': {'type': 'string'},
                        'country': {'type': 'string'},
                        'bio': {'type': 'string'},
                        'followers': {'type': 'string'}
                    }
                }
            }
        },
        400: {
            'description': '缺少since参数'
        },
        500: {
            'description': '服务器内部错误'
        }
    }
})
def recommend():
    since = request.args.get('since')
    if not since:
        logger.error(f"请求路径: {request.path} - 缺少since参数")
        return jsonify({"detail": "缺少since参数"}), 400
    try:
        # 获取推荐数据
        response_data = get_since_recommend(since)
        return jsonify(response_data[0]), response_data[1]
    except Exception as e:
        logger.error(f"处理推荐请求时出错: {e}")
        return jsonify({"detail": "服务器内部错误"}), 500
