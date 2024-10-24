import os

class Config:
    """
    配置类，用于从环境变量中读取配置项
    """
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
    DB_NAME = os.getenv('DB_NAME', 'to_github')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
