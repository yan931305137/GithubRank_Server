from contextlib import contextmanager
import json
from datetime import datetime

from info_service.config.db_config import Config
from info_service.utils.logger_utils import logger
from info_service.utils.mysql_utils import MySQLPool

# 使用配置文件中的数据库连接信息
pool = MySQLPool(
    host_name=Config.DB_HOST,
    user_name=Config.DB_USER,
    user_password=Config.DB_PASSWORD,
    db_name=Config.DB_NAME
)


def ensure_connection():
    """
    确保数据库连接是有效的，如果无效则重新连接。
    """
    global pool
    try:
        connection = pool.get_connection()
        connection.ping(reconnect=True)
        pool.release_connection(connection)
    except Exception as e:
        logger.error(f"数据库连接失败，尝试重新连接: {e}")
        pool = MySQLPool(
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
    ensure_connection()  # 确保连接有效
    connection = pool.get_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
        connection.commit()  # 添加提交操作
    except Exception as e:
        connection.rollback()  # 添加回滚操作
        raise e
    finally:
        cursor.close()
        pool.release_connection(connection)


def get_github_id(github_id):
    """
    根据github_id查询用户信息
    :param github_id: GitHub用户ID
    :return: 查询结果,成功返回用户信息,失败返回False,未找到返回None
    """
    try:
        query = "SELECT * FROM Github WHERE github_id = %s"
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (github_id,))
            result = cursor.fetchone()
            if result:
                # 遍历 result 字典，将 datetime 对象转为字符串
                for key, value in result.items():
                    if isinstance(value, datetime):
                        result[key] = value.isoformat()  # 转为字符串格式
                return json.dumps(result, ensure_ascii=False)
            else:
                return None
    except Exception as e:
        logger.error(f"查询github_id失败: {e}")
        return False


def get_rank_data():
    """
    获取GitHub用户排名数据
    :return: 排名数据字典
    """
    try:
        query = """
            SELECT github_id, user_info, evaluate 
            FROM github 
            WHERE evaluate IS NOT NULL
            ORDER BY CAST(JSON_EXTRACT(evaluate, '$.rank') AS SIGNED) ASC
            LIMIT 100
        """
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        rank_data = {
            'top_users': [
                {
                    'github_id': row['github_id'],
                    'user_info': json.loads(row['user_info']) if row['user_info'] else {},
                    'evaluate': json.loads(row['evaluate']) if row['evaluate'] else {}
                }
                for row in results
            ]
        }
        return rank_data
    except Exception as e:
        logger.error(f"获取排名数据失败: {e}")
        return None


def save_user_data(info_id, user_data):
    """
    保存用户基本信息
    :param info_id: GitHub用户ID
    :param user_data: 用户信息数据
    :return: 保存成功返回True,失败返回False
    """
    try:
        query = """
            INSERT INTO github (github_id, user_info, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                user_info = %s,
                updated_at = NOW()
        """
        user_data_json = json.dumps(user_data)
        with get_cursor(False) as cursor:
            cursor.execute(query, (info_id, user_data_json, user_data_json))
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False


def save_user_reops_data(info_id, user_repos_data):
    """
    保存用户仓库信息
    :param info_id: GitHub用户ID
    :param user_repos_data: 用户仓库数据
    :return: 保存成功返回True,失败返回False
    """
    try:
        query = """
            INSERT INTO github (github_id, repos_info, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                repos_info = %s,
                updated_at = NOW()
        """
        repos_data_json = json.dumps(user_repos_data)
        with get_cursor() as cursor:
            cursor.execute(query, (info_id, repos_data_json, repos_data_json))
        return True
    except Exception as e:
        logger.error(f"保存用户仓库数据失败: {e}")
        return False


def save_user_issues_data(info_id, issues):
    try:
        query = """
               INSERT INTO github (github_id, issues_info, updated_at)
               VALUES (%s, %s, NOW())
               ON DUPLICATE KEY UPDATE 
                   issues_info = %s,
                   updated_at = NOW()
           """
        issues_data_json = json.dumps(issues)
        with get_cursor() as cursor:
            cursor.execute(query, (info_id, issues_data_json, issues_data_json))
        return True
    except Exception as e:
        logger.error(f"保存用户仓库数据失败: {e}")
        return False


def save_user_tech_info_data(info_id, tech_stack):
    """
    保存用户技术栈信息
    :param info_id: GitHub用户ID
    :param tech_stack: 技术栈数据
    :return: 保存成功返回True,失败返回False
    """
    try:
        query = """
            INSERT INTO github (github_id, tech_stack, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                tech_stack = %s,
                updated_at = NOW()
        """
        tech_stack_json = json.dumps(tech_stack)
        with get_cursor(False) as cursor:
            cursor.execute(query, (info_id, tech_stack_json, tech_stack_json))
        return True
    except Exception as e:
        logger.error(f"保存用户技术栈数据失败: {e}")
        return False


def save_user_guess_nation_info_data(info_id, most_common_language):
    """
    保存用户语言使用信息
    :param info_id: GitHub用户ID
    :param most_common_language: 最常用语言数据
    :return: 保存成功返回True,失败返回False
    """
    try:
        query = """
            INSERT INTO github (github_id, most_common_language, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                most_common_language = %s,
                updated_at = NOW()
        """
        language_json = json.dumps(most_common_language)
        with get_cursor(False) as cursor:
            cursor.execute(query, (info_id, language_json, language_json))
        return True
    except Exception as e:
        logger.error(f"保存用户语言数据失败: {e}")
        return False


def save_evaluate_info(info_id, evaluate):
    """
    保存用户评估信息
    :param info_id: GitHub用户ID
    :param evaluate: 评估数据
    :return: 保存成功返回True,失败返回False
    """
    try:
        query = """
            INSERT INTO github (github_id, evaluate, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                evaluate = %s,
                updated_at = NOW()
        """
        evaluate_json = json.dumps(evaluate)
        with get_cursor(False) as cursor:
            cursor.execute(query, (info_id, evaluate_json, evaluate_json))
        return True
    except Exception as e:
        logger.error(f"保存用户评价数据失败: {e}")
        return False


def save_user_summary_info_data(info_id, summa):
    """
    保存用户总结信息
    :param info_id: GitHub用户ID
    :param summa: 总结数据
    :return: 保存成功返回True,失败返回False
    """
    try:
        query = """
            INSERT INTO github (github_id, summa, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                summa = %s,
                updated_at = NOW()
        """
        summa_json = json.dumps(summa)
        with get_cursor(False) as cursor:
            cursor.execute(query, (info_id, summa_json, summa_json))
        return True
    except Exception as e:
        logger.error(f"保存用户总结数据失败: {e}")
        return False
