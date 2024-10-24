from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    """
    用户类，表示一个用户的基本信息。

    属性:
        id (int): 用户ID
        username (str): 用户名
        email (str): 用户邮箱
        password_hash (str): 用户密码哈希
        github_id (str): GitHub ID
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """
    id: int
    username: str
    email: str
    password_hash: str
    github_id: str
    created_at: datetime
    updated_at: datetime
