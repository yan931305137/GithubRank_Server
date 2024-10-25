from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Github:
    id: Optional[int] = None  # 自增ID，可能在创建时未设置
    github_id: str = ''  # GitHub用户的唯一标识符
    user_info: Optional[Dict[str, Any]] = field(default_factory=dict)  # 用户详细信息
    repos_info: Optional[Dict[str, Any]] = field(default_factory=dict)  # 用户仓库信息
    tech_stack: Optional[Dict[str, Any]] = field(default_factory=dict)  # 用户技术栈信息
    most_common_language: Optional[str] = None  # 用户最常用的编程语言
    total: Optional[Dict[str, Any]] = field(default_factory=dict)  # 用户的总计信息
    summa: Optional[str] = None  # 用户的总结信息
    created_at: datetime = field(default_factory=datetime.utcnow)  # 创建时间
    updated_at: datetime = field(default_factory=datetime.utcnow)  # 更新时间
