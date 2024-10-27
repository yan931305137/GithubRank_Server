from flasgger import swag_from
from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from swagger_service.config.config import SERVICE_URLS
from swagger_service.utils.swagger_utils import get_swagger_spec, merge_swagger_specs

# 创建一个蓝图
swagger_bp = Blueprint('swagger', __name__)


def register_swagger_blueprint(app):
    # 注册路由蓝图
    app.register_blueprint(swagger_bp)
    swaggerui_blueprint = get_swaggerui_blueprint(
        '/swagger',
        '/swagger.json',
        config={'app_name': "分布式API聚合"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix='/swagger')


@swagger_bp.route('/swagger.json', methods=['GET'])
@swag_from({
    'tags': ['Swagger'],
    'responses': {
        200: {
            'description': '返回合并后的Swagger文档'
        },
        500: {
            'description': '获取或合并Swagger文档失败'
        }
    }
})
def swagger_json():
    try:
        # 获取Swagger JSON
        service_specs = {name: get_swagger_spec(url) for name, url in SERVICE_URLS.items()}
        # 合并Swagger文档
        combined_swagger = merge_swagger_specs(service_specs)
        return jsonify(combined_swagger), 200
    except Exception as e:
        return jsonify({"error": f"获取或合并Swagger文档失败: {str(e)}"}), 500
