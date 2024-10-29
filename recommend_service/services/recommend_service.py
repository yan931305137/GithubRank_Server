from contextlib import contextmanager
import json

from recommend_service.config.db_config import Config
from recommend_service.utils.logger_utils import logger
from recommend_service.utils.mysql_utils import create_connection

# 使用配置文件中的数据库连接信息
connection = create_connection(
    host_name=Config.DB_HOST,
    user_name=Config.DB_USER,
    user_password=Config.DB_PASSWORD,
    db_name=Config.DB_NAME
)


@contextmanager
def get_cursor(dictionary=False):
    """
    获取数据库游标的上下文管理器
    :param dictionary: 是否返回字典格式的结果
    :return: 数据库游标
    """
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
    except Exception as e:
        logger.error(f"获取数据库游标失败: {e}")
        raise
    finally:
        cursor.close()


def get_weekly_recommendations(weekly):
    """
    获取指定周的推荐数据
    :param weekly: 周期标识
    :return: 推荐数据的 JSON 对象或 None
    """
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM recommend WHERE weekly = %s", (weekly,))
            result = cursor.fetchone()
            if result:
                return json.loads(result['recommendations'])
            return None
    except Exception as e:
        logger.error(f"获取周推荐数据失败: {e}")
        return None


def save_weekly_recommendations(weekly, recommendations):
    """
    保存指定周的推荐数据
    :param weekly: 周期标识
    :param recommendations: 推荐数据的 JSON 对象
    :return: 操作是否成功
    """
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO recommend (weekly, recommendations)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE recommendations = VALUES(recommendations)
                """,
                (weekly, json.dumps(recommendations))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False
