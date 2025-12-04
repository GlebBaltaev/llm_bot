import asyncpg
import asyncio

async def clear_tables():
    try:
        # Создаем пул подключений
        async with asyncpg.create_pool(
            user='db_admin',
            password='admin',
            database='db2',
            host='127.0.0.1',
            min_size=1,
            max_size=5
        ) as pool:
            # Очищаем таблицы
            async with pool.acquire() as conn:
                # Очищаем users_treads
                await conn.execute("TRUNCATE TABLE users_treads")
                # Очищаем dialogs_history
                await conn.execute("TRUNCATE TABLE dialogs_history")
                
                print("Таблицы успешно очищены")
                
    except Exception as e:
        print(f"Ошибка при очистке таблиц: {e}")

# Запускаем асинхронную функцию
asyncio.run(clear_tables())