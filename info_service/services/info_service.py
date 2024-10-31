from contextlib import contextmanager
import json

from info_service.config.db_config import Config
from info_service.utils.logger_utils import logger
from info_service.utils.mysql_utils import MySQLPool

# 使用配置文件中的数据库连接信息
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
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
    finally:
        cursor.close()


def get_github_id(github_id):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT * FROM github WHERE github_id = %s
                """,
                (github_id,)
            )
            result = cursor.fetchone()
            if result:
                return result
            else:
                return None
    except Exception as e:
        logger.error(f"查询github_id失败: {e}")
        return False


def get_rank_data():
    try:
        # 这里可以添加获取排名数据的逻辑
        rank_data = {}  # 示例数据
        return rank_data
    except Exception as e:
        logger.error(f"获取排名数据失败: {e}")
        return None


def save_user_data(info_id, user_data):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, user_info)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE user_info = VALUES(user_info)
                """,
                (info_id, json.dumps(user_data))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False


def save_user_reops_data(info_id, user_repos_data):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, repos_info)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE repos_info = VALUES(repos_info)
                """,
                (info_id, json.dumps(user_repos_data))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False


def save_user_total_info_data(info_id, data):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, total)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE total = VALUES(total)
                """,
                (info_id, json.dumps(data))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False


def save_user_tech_info_data(info_id, tech_stack):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, tech_stack)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE tech_stack = VALUES(tech_stack)
                """,
                (info_id, json.dumps(tech_stack))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False


def save_user_guess_nation_info_data(info_id, most_common_language):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, most_common_language)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE most_common_language = VALUES(most_common_language)
                """,
                (info_id, json.dumps(most_common_language))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False


def save_evaluate_info(info_id, evaluate):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, evaluate)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE evaluate = VALUES(evaluate)
                """,
                (info_id, json.dumps(evaluate))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户评价数据失败: {e}")
        return False


def save_user_summary_info_data(info_id, summa):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO github (github_id, summa)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE summa = VALUES(summa)
                """,
                (info_id, json.dumps(summa))
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False
