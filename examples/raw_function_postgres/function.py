import psycopg2


def handler(event, context):
    connection = psycopg2.connect(
        database="akfg8iemf1lcfnom4019", # Идентификатор подключения
        user="user1", # Пользователь БД
        password=context.token["access_token"],
        host="akfg8iemf1lcfnom4019.postgresql-proxy.serverless.yandexcloud.net", # Точка входа
        port=6432,
        sslmode="require")
    cursor = connection.cursor()
    cursor.execute("SELECT 42;")
    record = cursor.fetchall()
    return record
