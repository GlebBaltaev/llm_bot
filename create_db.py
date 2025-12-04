import asyncio
import asyncpg

async def setup_database_dialogs_history():
    # Подключение к PostgreSQL как суперпользователь
    conn = await asyncpg.connect(user="db_admin", password="admin", database="postgres", host="127.0.0.1", port=5432)

    # Название новой базы данных, пользователя и пароля
    new_database = "db"
    user = "db_admin"
    new_password = "admin"

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

    # Подключение к новой базе данных как новый пользователь
    conn = await asyncpg.connect(user=user, password=new_password, database=new_database, host="127.0.0.1", port=5432)

    # Создание таблицы в новой базе данных
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS dialogs_history (
            id SERIAL PRIMARY KEY,
            id_tread TEXT NOT NULL,
            user_message TEXT NOT NULL,
            llm_response TEXT NOT NULL,
            model_code TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)
    print("Таблица 'dialogs_hisrory' создана.")

    # Закрытие соединения
    await conn.close()

async def setup_database_users_treads():
    # Подключение к PostgreSQL как суперпользователь
    conn = await asyncpg.connect(user="db_admin", password="admin", database="postgres", host="127.0.0.1", port=5432)

    # Название новой базы данных, пользователя и пароля
    new_database = "db"
    user = "db_admin"
    new_password = "admin"

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

    # Закрытие соединения
    await conn.close()

async def main():
    await setup_database_dialogs_history()
    await setup_database_users_treads()
# Запуск функции
asyncio.run(main())

