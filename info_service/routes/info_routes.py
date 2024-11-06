from flasgger import Swagger, swag_from

from flask import jsonify, request, Blueprint

from info_service.utils.actor_utils import run_actor
from info_service.utils.logger_utils import logger

from info_service.controllers.info_controller import InfoController

# 定义蓝图
info_bp = Blueprint('info', __name__)


# 在主应用中注册蓝图
def register_info_blueprint(app):
    app.register_blueprint(info_bp, url_prefix='/info')
    Swagger(app)


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
    response = InfoController.get_user_info(github_id)
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
def repos_info():
    """
    获取单个github用户信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400

    logger.info(f"获取用户信息请求已收到，github_id: {github_id}")
    response = InfoController.get_user_repos_info(github_id)
    logger.info(f"获取用户信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/issueInfo', methods=['GET'])
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
            'description': '获取用户issue信息成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'repo_name': {
                                    'type': 'string',
                                    'example': 'example_repo'
                                },
                                'issue_title': {
                                    'type': 'string',
                                    'example': 'Fix bug'
                                },
                                'issue_url': {
                                    'type': 'string',
                                    'example': 'https://github.com/user/repo/issues/1'
                                },
                                'created_at': {
                                    'type': 'string',
                                    'example': '2023-01-01 12:00:00'
                                },
                                'state': {
                                    'type': 'string',
                                    'example': 'open'
                                }
                            }
                        }
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
def issue_info():
    """
    获取单个github用户的issue信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.path} - 缺少github_id参数")
        return jsonify({"detail": "缺少github_id参数"}), 400

    try:
        logger.info(f"获取用户issue信息请求已收到，github_id: {github_id}")
        response = InfoController.get_user_issue_info(github_id)
        logger.info(f"获取用户issue信息请求处理完毕，github_id: {github_id}")
        return jsonify(response[0]), response[1]
    except Exception as e:
        logger.error(f"获取用户issue信息时发生错误，github_id: {github_id}，错误信息: {str(e)}")
        return jsonify({"detail": "服务器内部错误"}), 500


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
    response = InfoController.get_user_tech_info(github_id)
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
    response = InfoController.get_user_guess_nation_info(github_id)
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
    response = InfoController.get_user_summary_info(github_id)
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
        response_data = InfoController.get_evaluate_info(github_id)
        logger.info(f"获取用户评分请求处理完毕，user: {github_id}")
        return jsonify(response_data[0]), response_data[1]
    except Exception as e:
        logger.error(f"获取用户评分时发生错误，user: {github_id}，错误信息: {str(e)}")
        return jsonify({"detail": "服务器内部错误"}), 500


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
def total_info():
    """
    获取单个github用户项目信息
    :return: 响应数据
    """
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(request.path)
        return jsonify({"detail": "缺少github_id参数"}), 400

    logger.info(f"获取用户项目信息请求已收到，github_id: {github_id}")
    response = InfoController.get_user_total_info(github_id)
    logger.info(f"获取用户项目信息请求处理完毕，github_id: {github_id}")
    return jsonify(response[0]), response[1]


@info_bp.route('/search', methods=['GET'])
@swag_from({
    'tags': ['信息服务'],
    'parameters': [
        {
            'name': 'keyword',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': '搜索关键词'
        },
        {
            'name': 'target_language',
            'in': 'query',
            'required': False,
            'type': 'string',
            'description': '目标编程语言'
        },
        {
            'name': 'techs',
            'in': 'query',
            'required': False,
            'type': 'array',
            'items': {
                'type': 'string'
            },
            'description': '技术栈列表'
        },
        {
            'name': 'pagesize',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': '每页数量'
        },
        {
            'name': 'curpage',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': '当前页码'
        }
    ],
    'responses': {
        200: {
            'description': '搜索成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'total': {
                        'type': 'integer',
                        'description': '总记录数',
                        'example': 100
                    },
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'repo_name': {
                                    'type': 'string',
                                    'example': 'example_repo'
                                },
                                'description': {
                                    'type': 'string',
                                    'example': '项目描述'
                                },
                                'language': {
                                    'type': 'string',
                                    'example': 'Python'
                                },
                                'stars': {
                                    'type': 'integer',
                                    'example': 100
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': '参数错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                        'example': '缺少必要参数'
                    }
                }
            }
        }
    }
})
def search():
    """
    搜索GitHub项目
    :return: 响应数据
    """
    keyword = request.args.get('keyword')
    if not keyword:
        logger.error("缺少keyword参数")
        return jsonify({"detail": "缺少keyword参数"}), 400

    pagesize = int(request.args.get('pagesize', 20))
    curpage = int(request.args.get('curpage', 1))

    target_language = request.json.get('target_language')
    techs = request.json.get('techs')

    logger.info(f"搜索请求已收到，keyword: {keyword}, language: {target_language}, techs: {techs}")
    response = run_actor(keyword, target_language, techs, 80, curpage, pagesize * 10)
    logger.info(f"搜索请求处理完毕，keyword: {keyword}")

    print(response)
    return {"result": response}, 200
