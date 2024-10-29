from flasgger import Swagger, swag_from

from flask import jsonify, request, Blueprint

from info_service.utils.logger_utils import logger

from info_service.controllers.info_controller import get_github_rank, get_user_info, get_user_repos_info, \
    get_user_total_info, get_user_tech_info, get_user_guess_nation_info, get_user_summary_info, get_evaluate_info

# 定义蓝图
info_bp = Blueprint('info', __name__)


# 在主应用中注册蓝图
def register_info_blueprint(app):
    app.register_blueprint(info_bp, url_prefix='/info')
    Swagger(app)


@info_bp.route('/rank', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'responses': {
        200: {
            'description': '获取githubRank成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'rank': {
                        'type': 'integer',
                        'example': 1
                    }
                }
            }
        }
    }
})
def rank():
    """
    获取githubRank
    :return: 响应数据
    """
    logger.info("获取githubRank请求已收到")
    response = get_github_rank()
    logger.info("获取githubRank请求处理完毕")
    return jsonify(response[0]), response[1]


@info_bp.route('/userInfo', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户信息成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'example_user'
                    },
                    'email': {
                        'type': 'string',
                        'example': 'user@example.com'
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        }
    }
})
def user_info():
    """
    获取单个github用户信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400

    logger.info(f"获取用户信息请求已收到，github_id: {github_id}")
    response = get_user_info(github_id)
    logger.info(f"获取用户信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/reposInfo', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户项目信息成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'repo_name': {
                        'type': 'string',
                        'example': 'example_repo'
                    },
                    'stars': {
                        'type': 'integer',
                        'example': 100
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        }
    }
})
def repos_info():
    """
    获取单个github用户项目信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400

    logger.info(f"获取用户项目信息请求已收到，github_id: {github_id}")
    response = get_user_repos_info(github_id)
    logger.info(f"获取用户项目信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/total', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户项目总数信息成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'total_stars': {
                        'type': 'integer',
                        'example': 500
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        }
    }
})
def total_info():
    """
    获取单个github用户项目stars等总数信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400
    user_id = request.args.get('github_id')
    logger.info(f"获取用户项目总数信息请求已收到，github_id: {user_id}")
    response = get_user_total_info(user_id)
    logger.info(f"获取用户项目总数信息请求处理完毕，github_id: {user_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/techInfo', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户技术栈信息成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'tech_stack': {
                        'type': 'string',
                        'example': 'Python, JavaScript'
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        }
    }
})
def tech_info():
    """
    获取单个github用户技术栈信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400
    logger.info(f"获取用户技术栈信息请求已收到，github_id: {github_id}")
    response = get_user_tech_info(github_id)
    logger.info(f"获取用户技术栈信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/guessNation', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户国家信息猜测成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'nation': {
                        'type': 'string',
                        'example': 'USA'
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        }
    }
})
def guess_nation():
    """
    获取单个github用户国家信息猜测
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400
    logger.info(f"获取用户国家信息猜测请求已收到，github_id: {github_id}")
    response = get_user_guess_nation_info(github_id)
    logger.info(f"获取用户国家信息猜测请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/summary', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户评价信息成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'summary': {
                        'type': 'string',
                        'example': 'This user is very active on GitHub.'
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        }
    }
})
def summary():
    """
    获取单个github用户基于gpt的评价信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400
    logger.info(f"获取用户评价信息请求已收到，github_id: {github_id}")
    response = get_user_summary_info(github_id)
    logger.info(f"获取用户评价信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/evaluate', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '获取用户评分成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'score': {
                        'type': 'integer',
                        'example': 5
                    }
                }
            }
        },
        400: {
            'description': '缺少github_id参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少github_id参数'
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '服务器内部错误'
                    }
                }
            }
        }
    }
})
def get_evaluate():
    """
     获取用户评分
     :return: JSON响应数据
     """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.path} - 缺少github_id参数")
        return jsonify({"detail": "缺少github_id参数"}), 400

    try:
        # 获取用户评分
        response_data = get_evaluate_info(github_id)
        logger.info(f"获取用户评分请求处理完毕，user: {github_id}")
        return jsonify(response_data[0]), response_data[1]
    except Exception as e:
        logger.error(f"获取用户评分时发生错误，user: {github_id}，错误信息: {str(e)}")
        return jsonify({"detail": "服务器内部错误"}), 500


