from contextlib import contextmanager
import json

from recommend_service.config.db_config import Config
from recommend_service.utils.logger_utils import logger
from recommend_service.utils.mysql_utils import MySQLPool

# 使用配置文件中的数据库连接信息
connection = MySQLPool(
    host_name=Config.DB_HOST,
    user_name=Config.DB_USER,
    user_password=Config.DB_PASSWORD,
    db_name=Config.DB_NAME
).get_connection()


def ensure_connection():
    """
    确保数据库连接是有效的，如果无效则重新连接。
    """
    global connection
    try:
        connection.ping(reconnect=True)
    except Exception as e:
        logger.error(f"数据库连接失败，尝试重新连接: {e}")
        connection = MySQLPool(
            host_name=Config.DB_HOST,
            user_name=Config.DB_USER,
            user_password=Config.DB_PASSWORD,
            db_name=Config.DB_NAME
        ).get_connection()


@contextmanager
def get_cursor(dictionary=False):
    """
    获取数据库游标的上下文管理器
    :param dictionary: 是否返回字典格式的结果
    :return: 数据库游标
    """
    ensure_connection()  # 确保连接有效
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
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
            cursor.execute("SELECT * FROM weekly_recommend WHERE weekly = %s", (weekly,))
            result = cursor.fetchone()
            if result:
                return json.loads(result['recommendations'])
            return None
    except Exception as e:
        logger.error(f"获取周推荐数据失败: {e}")
        return None


def get_daily_recommendations(daily):
    """
    获取指定日的推荐数据
    :param daily: 周期标识
    :return: 推荐数据的 JSON 对象或 None
    """
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM daily_recommend WHERE daily = %s", (daily,))
            result = cursor.fetchone()
            if result:
                return json.loads(result['recommendations'])
            return None
    except Exception as e:
        logger.error(f"获取日推荐数据失败: {e}")
        return None


def get_monthly_recommendations(monthly):
    """
    获取指定月的推荐数据
    :param monthly: 周期标识
    :return: 推荐数据的 JSON 对象或 None
    """
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM monthly_recommend WHERE monthly = %s", (monthly,))
            result = cursor.fetchone()
            if result:
                return json.loads(result['recommendations'])
            return None
    except Exception as e:
        logger.error(f"获取月推荐数据失败: {e}")
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
                INSERT INTO weekly_recommend (weekly, recommendations)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE recommendations = VALUES(recommendations)
                """,
                (weekly, json.dumps(recommendations))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存周推荐数据失败: {e}")
        return False


def save_monthly_recommendations(monthly, recommendations):
    """
    保存指定月的推荐数据
    :param monthly: 周期标识
    :param recommendations: 推荐数据的 JSON 对象
    :return: 操作是否成功
    """
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO monthly_recommend (monthly, recommendations)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE recommendations = VALUES(recommendations)
                """,
                (monthly, json.dumps(recommendations))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存月推荐数据失败: {e}")
        return False


def save_daily_recommendations(daily, recommendations):
    """
    保存指定日的推荐数据
    :param daily: 周期标识
    :param recommendations: 推荐数据的 JSON 对象
    :return: 操作是否成功
    """
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO daily_recommend (daily, recommendations)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE recommendations = VALUES(recommendations)
                """,
                (daily, json.dumps(recommendations))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存日推荐数据失败: {e}")
        return False
