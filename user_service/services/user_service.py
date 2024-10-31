import mysql.connector
from contextlib import contextmanager

from user_service.config.db_config import Config
from user_service.utils.cryp_utils import decrypt_password
from user_service.utils.logger_utils import logger
from user_service.utils.mysql_utils import MySQLPool

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


def check_user_credentials(username, password):
    """
    检查用户凭证
    :param username: 用户名
    :param password: 密码
    :return: 如果凭证有效则返回True，否则返回False
    """
    with get_cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
    if user and decrypt_password(user['password']) == password:
        logger.info(f"用户 {username} 凭证验证成功")
        return True
    else:
        logger.warning(f"用户 {username} 凭证验证失败")
        return False


def create_user(username, password_hash):
    """
    创建新用户
    :param username: 用户名
    :param password_hash: 密码哈希值
    :raises ValueError: 如果用户已存在或其他错误
    """
    with get_cursor(dictionary=True) as cursor:
        try:
            # 检查用户名是否存在
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                logger.warning(f"尝试创建已存在的用户 {username}")
                raise ValueError("用户已存在")

            # 添加用户
            cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password_hash))
            connection.commit()
            logger.info(f"用户 {username} 创建成功")
        except mysql.connector.Error as err:
            connection.rollback()
            logger.error(f"创建用户 {username} 失败: {err}")
            raise ValueError("用户已存在或其他错误: {}".format(err))


def delete_user_by_id(user_id):
    """
    根据用户ID删除用户
    :param user_id: 用户ID
    :raises ValueError: 如果用户未找到或删除失败
    """
    with get_cursor(dictionary=True) as cursor:
        try:
            cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
            if cursor.rowcount == 0:
                logger.warning(f"尝试删除不存在的用户 ID {user_id}")
                raise ValueError("用户未找到")
            connection.commit()
            logger.info(f"用户 ID {user_id} 删除成功")
            return True
        except mysql.connector.Error as err:
            connection.rollback()
            logger.error(f"删除用户 ID {user_id} 失败: {err}")
            return False


def get_user_by_id(user_id):
    """
    根据用户ID获取用户信息
    :param user_id: 用户ID
    :return: 用户信息字典
    """
    with get_cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
    if user:
        logger.info(f"获取用户 ID {user_id} 信息成功")
    else:
        logger.warning(f"用户 ID {user_id} 不存在")
    return user


def service_update_user_by_id(user_id, data):
    """
    更新用户信息服务
    :param user_id: 用户ID
    :param data: 更新的数据
    :raises ValueError: 如果用户未找到或更新失败
    """
    with get_cursor(dictionary=True) as cursor:
        try:
            # 检查用户是否存在
            cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                logger.warning(f"尝试更新不存在的用户 ID {user_id}")
                raise ValueError("用户未找到")

            # 更新用户信息
            update_fields = ", ".join(f"{key} = %s" for key in data.keys())
            update_values = list(data.values()) + [user_id]
            cursor.execute(f"UPDATE user SET {update_fields} WHERE id = %s", update_values)
            connection.commit()
            logger.info(f"用户 ID {user_id} 信息更新成功")
        except mysql.connector.Error as err:
            connection.rollback()
            logger.error(f"更新用户 ID {user_id} 信息失败: {err}")
            raise ValueError("更新用户信息失败: {}".format(err))


def save_user_appraisal(username, github_id, message, point):
    try:
        with get_cursor(dictionary=True) as cursor:
            # 查询 user_id
            cursor.execute(
                """
                SELECT id FROM user WHERE username = %s
                """,
                (username,)
            )
            user = cursor.fetchone()

            if not user:
                logger.error(f"用户 {username} 不存在")
                return False

            user_id = user['id']

            # 插入评价数据
            cursor.execute(
                """
                INSERT INTO appraisal (user_id, github_id, rating, message)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, github_id, point, message)
            )
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"保存用户评价数据失败: {e}")
        return False


def get_user_appraisals(github_id):
    try:
        with get_cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT * FROM appraisal WHERE github_id = %s
                """,
                (github_id,)
            )
            appraisals = cursor.fetchall()
        return appraisals
    except Exception as e:
        logger.error(f"获取用户评估数据失败: {e}")
        return None
