from datetime import datetime, timedelta
import jwt
from functools import wraps


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
            # 验证JWT
            decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded_payload, None
        except jwt.ExpiredSignatureError:
            # 处理过期的签名
            return None, {'message': '令牌已过期!'}, 403  # 修改此行
        except jwt.InvalidTokenError:
            # 处理无效的令牌
            return None, {'message': '无效的令牌!'}, 403  # 修改此行


# 初始化JWT管理器
jwt_manager = JWTManager(secret_key='your_secret_key')


def token_required(f):
    """
    装饰器函数，用于保护需要令牌验证的路由
    :param f: 被装饰的函数
    :return: 装饰后的函数
    """

    @wraps(f)
    def decorated(request, *args, **kwargs):
        # 从请求头中获取令牌
        token = request.headers.get('Authorization')
        if not token:
            # 如果令牌缺失，返回错误信息
            return {'message': '令牌缺失!'}, 403
        # 验证令牌
        decoded_payload, error_response = jwt_manager.verify_token(token)
        if error_response:
            # 如果解码失败，返回错误信息
            return error_response
        return f(*args, **kwargs)

    return decorated
