import pymysql
import load_yaml


def connect():
    """
    连接mysql数据库
    :return:
    """
    server, port, name, username, password = load_yaml.get_mysql_info()
    # 打开数据库连接
    pymysql.connect()
    db = pymysql.connect(
        host=server,
        port=port,
        user=username,
        passwd=password,
        db=name,
        charset="utf-8"
    )
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("SELECT * FROM user")
    # 使用 fetchall() 方法获取所有数据.
    data = cursor.fetchall()
    print(data)
    # 关闭数据库连接
    db.close()
