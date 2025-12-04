import asyncio
import asyncpg

DATA_BASE = 'db2'


async def create_database(db=DATA_BASE):
    conn = await asyncpg.connect(user="db_admin", password="admin", database="postgres", host="127.0.0.1", port=5432)

    # Название новой базы данных, пользователя и пароля
    new_database = db
    user = "db_admin"

    # Создание базы данных
    try:
        await conn.execute(f'CREATE DATABASE {new_database}')
        print(f"База данных '{new_database}' создана.")
    except asyncpg.exceptions.DuplicateDatabaseError:
        print(f"База данных '{new_database}' уже существует.")


    # Назначение прав новому пользователю на новую базу данных
    await conn.execute(f"GRANT ALL PRIVILEGES ON DATABASE {new_database} TO {user}")
    print(f"Права на базу данных '{new_database}' назначены пользователю '{user}'.")

    # Закрытие соединения с суперпользователем
    await conn.close()

async def setup_database_dialogs_history(db=DATA_BASE):
    # Название новой базы данных, пользователя и пароля
    new_database = db
    user = "db_admin"
    new_password = "admin"

    # Подключение к новой базе данных как новый пользователь
    conn = await asyncpg.connect(user=user, password=new_password, database=new_database, host="127.0.0.1", port=5432)

    # Создание таблицы в новой базе данных
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS dialogs_history (
            id SERIAL PRIMARY KEY,
            id_tread TEXT NOT NULL,
            content TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Таблица 'dialogs_hisrory' создана.")

    # Закрытие соединения
    await conn.close()

async def setup_database_users_treads(db=DATA_BASE):
    # Название новой базы данных, пользователя и пароля
    new_database = db
    user = "db_admin"
    new_password = "admin"

    # Подключение к новой базе данных как новый пользователь
    conn = await asyncpg.connect(user=user, password=new_password, database=new_database, host="127.0.0.1", port=5432)

    # Создание таблицы в новой базе данных
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users_treads (
            id_user TEXT NOT NULL,
            id_tread TEXT NOT NULL,
            PRIMARY KEY (id_user, id_tread)
        )
    """)
    print("Таблица 'users_treads' создана.")

async def setup_database_tread_picture(db=DATA_BASE):
    new_database = db
    user = "db_admin"
    new_password = "admin"

    # Подключение к новой базе данных как новый пользователь
    conn = await asyncpg.connect(user=user, password=new_password, database=new_database, host="127.0.0.1", port=5432)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS tread_picture (
            id_tread TEXT NOT NULL,
            picture TEXT NOT NULL,
            PRIMARY KEY (id_tread, picture)
        )
    """)
    print("Таблица 'tread_picture' создана.")

    # Закрытие соединения
    await conn.close()

async def main():
    await create_database(DATA_BASE)
    await setup_database_dialogs_history(DATA_BASE)
    await setup_database_users_treads(DATA_BASE)
    await setup_database_tread_picture(DATA_BASE)
# Запуск функции
asyncio.run(main())

