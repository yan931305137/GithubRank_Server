import mysql
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    """
    创建数据库连接
    :param host_name: 数据库主机名
    :param user_name: 数据库用户名
    :param user_password: 数据库用户密码
    :param db_name: 数据库名称
    :return: 数据库连接对象
    """
    connect = None
    try:
        connect = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("成功连接到数据库")
    except Error as e:
        print(f"连接数据库时发生错误: {e}")
    return connect

def execute_query(connect, query):
    """
    执行数据库查询
    :param connect: 数据库连接对象
    :param query: 要执行的SQL查询
    """
    try:
        with connect.cursor() as cursor:
            cursor.execute(query)
            connect.commit()
            print("查询成功执行")
    except Error as e:
        print(f"执行查询时发生错误: {e}")

def fetch_query(connect, query):
    """
    获取查询结果
    :param connect: 数据库连接对象
    :param query: 要执行的SQL查询
    :return: 查询结果
    """
    result = []
    try:
        with connect.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    except Error as e:
        print(f"获取数据时发生错误: {e}")
    return result
