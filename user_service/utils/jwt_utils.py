from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request


class JWTManager:
    def __init__(self, secret_key, algorithm='HS256'):
        """
        初始化JWTManager类
        :param secret_key: 用于签名的密钥
        :param algorithm: 使用的算法，默认为HS256
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, payload, expiration_minutes=30):
        """
        生成JWT令牌
        :param payload: 令牌的负载信息
        :param expiration_minutes: 令牌的过期时间（分钟），默认为30分钟
        :return: 生成的JWT令牌
        """
        # 设置过期时间
        payload['exp'] = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        # 生成JWT
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token):
        """
        验证JWT令牌
        :param token: 要验证的JWT令牌
        :return: 解码后的负载信息和错误响应（如果有）
        """
        try:
            decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded_payload, None
        except jwt.ExpiredSignatureError:
            return None, {'message': '令牌已过期!'}
        except jwt.InvalidTokenError:
            return None, {'message': '无效的令牌!'}


# 初始化JWT管理器
jwt_manager = JWTManager(secret_key='your_secret_key')


def token_required(f):
    """
    装饰器函数，用于保护需要令牌验证的路由
    :param f: 被装饰的函数
    :return: 装饰后的函数
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        # 确保从请求中正确获取 token
        token = request.headers.get('Authorization')
        if not token:
            return {"error": "缺少Authorization token"}, 401

        # 验证 token
        ver, err = jwt_manager.verify_token(token)
        if err:
            return {"error": "无效的Authorization token"}, 403

        # 确保传递正确的参数给被装饰的函数
        return f(*args, **kwargs)

    return decorated
