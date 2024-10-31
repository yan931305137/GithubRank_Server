import mysql
from mysql.connector import Error


class MySQLPool:
    def __init__(self, host_name, user_name, user_password, db_name, pool_name="mypool", pool_size=5):
        self.dbconfig = {
            "host": host_name,
            "user": user_name,
            "password": user_password,
            "database": db_name
        }
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **self.dbconfig
        )

    def get_connection(self):
        try:
            connection = self.pool.get_connection()
            if connection.is_connected():
                print("成功从连接池获取连接")
                return connection
        except Error as e:
            print(f"从连接池获取连接时发生错误: {e}")
            return None

    def release_connection(self, connection):
        if connection.is_connected():
            connection.close()
            print("连接已释放回连接池")


def execute_query(pool, query):
    """
    执行数据库查询
    :param pool: 数据库连接池对象
    :param query: 要执行的SQL查询
    """
    connection = pool.get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                print("查询成功执行")
        except Error as e:
            print(f"执行查询时发生错误: {e}")
        finally:
            pool.release_connection(connection)


def fetch_query(pool, query):
    """
    获取查询结果
    :param pool: 数据库连接池对象
    :param query: 要执行的SQL查询
    :return: 查询结果
    """
    connection = pool.get_connection()
    result = []
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                # 确保读取所有结果集
                while True:
                    result.extend(cursor.fetchall())
                    if not cursor.nextset():
                        break
        except Error as e:
            print(f"获取数据时发生错误: {e}")
        finally:
            pool.release_connection(connection)
    return result
