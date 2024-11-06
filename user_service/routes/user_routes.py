import re
import urllib.parse

from flasgger import Swagger, swag_from

from flask import jsonify, request, Blueprint, session

from user_service.utils.logger_utils import logger

from user_service.controllers.user_controller import (
    login_user, register_user, delete_user_by_id, get_user_by_id, update_user_by_id,
    save_appraisal, get_appraisals
)

from user_service.utils.jwt_utils import token_required, jwt_manager

# 定义蓝图
user_bp = Blueprint('user', __name__)


# 在主应用中注册蓝图
def register_user_blueprint(app):
    app.register_blueprint(user_bp, url_prefix='/user')
    Swagger(app)


@user_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['用户认证'],
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'example_user'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'password123'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '用户登录成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'token': {
                        'type': 'string',
                        'description': '用户的 JWT token'
                    }
                }
            }
        },
        400: {
            'description': '请求参数错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '用户名或密码错误'
                    }
                }
            }
        }
    }
})
def login():
    data = request.json
    logger.info(f"登录请求数据: {data}")
    response = login_user(data)
    logger.info(f"登录响应数据: {response}")
    if response[1] == 200:
        logger.info("用户登录成功")
    else:
        logger.error("用户登录失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['用户认证'],
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'new_user'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'new_password123'
                    },
                    'email': {
                        'type': 'string',
                        'example': 'user@example.com'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': '用户注册成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': '注册成功'
                    }
                }
            }
        },
        400: {
            'description': '请求参数错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '缺少必要参数'
                    }
                }
            }
        },
        409: {
            'description': '用户已存在',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '用户已存在'
                    }
                }
            }
        }
    }
})
def register():
    data = request.json
    logger.info(f"注册请求数据: {data}")
    response = register_user(data)
    logger.info(f"注册响应数据: {response}")
    if response[1] == 201:
        logger.info("用户注册成功")
    else:
        logger.error("用户注册失败")
    return jsonify(response[0]), response[1]


@user_bp.route('/delete', methods=['DELETE'])
@swag_from({
    'tags': ['用户管理'],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'query',  # 确保这里是 'query' 而不是 'path'
            'required': True,
            'type': 'integer',
            'description': '要删除的用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '用户删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': '用户删除成功'
                    }
                }
            }
        },
        404: {
            'description': '用户未找到',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '用户未找到'
                    }
                }
            }
        },
        401: {
            'description': '未授权',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '未授权'
                    }
                }
            }
        }
    }
})
def delete_user():
    user_id = request.args.get('user_id')
    if not user_id:
        logger.error(request.path)
        return jsonify({"detail": "user_id"}), 400

    response = delete_user_by_id(user_id)
    if response[1] == 200:
        logger.info("用户删除成功")
        return jsonify(response[0]), response[1]
    else:
        logger.error("用户删除失败")
        return jsonify(response[0]), response[1]


@user_bp.route('/get', methods=['GET'])
@swag_from({
    'tags': ['用户管理'],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': '要查询的用户ID'
        }
    ],
    'responses': {
        200: {
            'description': '用户查询成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': '用户123'
                    },
                    'email': {
                        'type': 'string',
                        'example': 'user@example.com'
                    },
                    'other_property': {
                        'type': 'string',
                        'example': '其他属性值'
                    }
                }
            }
        },
        404: {
            'description': '用户未找到',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '用户未找到'
                    }
                }
            }
        },
        401: {
            'description': '未授权',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '未授权'
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '服务器内部错误'
                    }
                }
            }
        }
    }
})
def get_user():
    user_id = request.args.get('user_id')
    if not user_id:
        logger.error(request.path)
        return jsonify({"detail": "user_id"}), 400

    logger.info(f"查询用户ID: {user_id}")
    response = get_user_by_id(user_id)
    if response[1] == 200:
        logger.info("用户查询成功")
        return jsonify(response[0]), response[1]
    else:
        logger.error("用户查询失败")
        return jsonify(response[0]), response[1]


@user_bp.route('/update', methods=['PUT'])
@swag_from({
    'tags': ['用户管理'],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': '要更新的用户ID'
        },
        {
            'name': 'data',
            'in': 'body',
            'required': True,
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
                    },
                    'other_property': {
                        'type': 'string',
                        'example': '其他属性值'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '用户更新成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': '用户信息更新成功'
                    }
                }
            }
        },
        400: {
            'description': '用户名错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '用户名错误'
                    }
                }
            }
        },
        401: {
            'description': '未授权',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '未授权'
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '服务器内部错误'
                    }
                }
            }
        }
    }
})
def update_user():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            logger.error(request.path)
            return jsonify({"detail": "user_id"}), 400

        data = request.json
        logger.info(f"更新用户ID: {user_id}，请求数据: {data}")

        token = request.headers.get('Authorization')
        decoded_payload, error_response = jwt_manager.verify_token(token)
        if error_response:
            logger.warning(f"更新用户信息失败: 用户ID={user_id}, 错误信息: {error_response}")
            return jsonify(error_response), 401

        username = decoded_payload.get('username')
        if username != data.get('username'):
            logger.warning(
                f"用户名错误: 用户ID={user_id}, 提供的用户名={data.get('username')}, 令牌中的用户名={username}"
            )
            return jsonify({"error": "用户名错误"}), 400

        response = update_user_by_id(user_id, data)
        if response[1] == 200:
            logger.info("用户更新成功")
            return jsonify({'message': '用户信息更新成功'}), 200
        else:
            logger.error("用户更新失败")
            return jsonify(response[0]), response[1]
    except Exception as e:
        logger.error(f"更新用户时发生错误，用户ID: {user_id}，错误信息: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@user_bp.route('/appraise', methods=['POST'])
@swag_from({
    'tags': ['用户评价'],
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'score': {
                        'type': 'integer',
                        'example': 5
                    },
                    'comment': {
                        'type': 'string',
                        'example': '非常优秀的项目'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '评价成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': '评价成功'
                    }
                }
            }
        },
        401: {
            'description': '未授权',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '缺少 Authorization token'
                    }
                }
            }
        },
        403: {
            'description': '无效的 Authorization token',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '无效的 Authorization token'
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '服务器内部错误'
                    }
                }
            }
        }
    }
})
def appraise():
    try:
        user_info = request.cookies.get('user_info')
        if not user_info:
            logger.warning("用户未登录")
            return jsonify({"error": "请先登录"}), 401

        print(user_info)

        # 解码 URL 编码的字符串
        decoded_user_info = urllib.parse.unquote(user_info)
        
        pattern = r'"login":"(.*?)"'        
        username = None
        match = re.search(pattern, decoded_user_info)
        if match:
            username = match.group(1)

        if not username:
            logger.warning("无法获取用户名")
            return jsonify({"error": "无法获取用户名"}), 401

        # 注册用户
        data = {
            "username": username,
            "password": username
        }
        response = register_user(data)

        data = request.json
        if not data:
            logger.warning("缺少评价数据")
            return jsonify({"error": "缺少评价数据"}), 400

        # 验证评价数据
        score = data.get('number')
        comment = data.get('message')

        if score is None or not isinstance(score, int) or score < 1 or score > 5:
            logger.warning(f"无效的评分: {score}")
            return jsonify({"error": "评分必须是1-5之间的整数"}), 400

        if not comment or not isinstance(comment, str):
            logger.warning("无效的评价内容")
            return jsonify({"error": "评价内容不能为空"}), 400

        # 保存评价
        logger.info(f"用户评价请求已收到，用户: {username}, 数据: {data}")
        response = save_appraisal(username, data)

        if response[1] != 200:
            logger.error(f"保存评价失败: {response[0]}")
            return jsonify(response[0]), response[1]

        logger.info("用户评价保存成功")
        return jsonify({"message": "评价成功"}), 200

    except Exception as e:
        logger.error(f"处理评价请求时发生错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@user_bp.route('/getAppraise', methods=['GET'])
@swag_from({
    'tags': ['用户评价'],
    'parameters': [
        {
            'name': 'github_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'GitHub 用户ID'
        },
        {
            'name': 'pagesize',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': '每页数量,默认20'
        },
        {
            'name': 'curpage',
            'in': 'query', 
            'required': False,
            'type': 'integer',
            'description': '当前页码,默认1'
        }
    ],
    'responses': {
        200: {
            'description': '返回用户的评价列表',
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
                                'score': {
                                    'type': 'integer',
                                    'example': 5
                                },
                                'comment': {
                                    'type': 'string',
                                    'example': '非常优秀的项目'
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': '缺少 github_id 参数',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '缺少 github_id 参数'
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': '服务器内部错误'
                    }
                }
            }
        }
    }
})
def get_appraise():
    github_id = request.args.get('github_id')
    if not github_id:
        logger.error(f"请求路径: {request.url} - 缺少 github_id 参数")
        return jsonify({"error": "缺少 github_id 参数"}), 400

    # 获取分页参数
    pagesize = int(request.args.get('pagesize', 20))
    curpage = int(request.args.get('curpage', 1))

    try:
        response_data = get_appraisals(github_id,pagesize,curpage)
        if response_data[1] != 200:
            return jsonify(response_data[0]), response_data[1]

        logger.info(f"获取用户评价请求处理完毕，user: {github_id}")
        return response_data[0], 200
    except Exception as e:
        logger.error(f"获取用户评价时发生错误，user: {github_id}，错误信息: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500
