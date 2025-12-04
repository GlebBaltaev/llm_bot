import asyncio
import asyncpg

async def insert_data(id_tread, user_message, llm_responce, model_code, time = None):
    try:
        if not time:
            conn = await asyncpg.connect(
                user='db_admin',
                password='admin',
                database='db',
                host='127.0.0.1'
            )
            await conn.execute(
                """
                INSERT INTO dialogs_history (id_tread, user_message, llm_response, model_code)
                VALUES ($1, $2, $3, $4)
                """,
                id_tread,
                user_message,
                llm_responce,
                model_code
            )
            await conn.close()
        else:
            conn = await asyncpg.connect(
                user='db_admin',
                password='admin',
                database='db',
                host='127.0.0.1'
            )
            await conn.execute(
                """
                INSERT INTO dialogs_history (id_tread, user_message, llm_response, model_code, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                """,
                id_tread,
                user_message,
                llm_responce,
                model_code,
                time
            )
            await conn.close()
    except Exception as e:
        print(f"Ошибка при записи данных: {e}")

async def fetch_history(id_tread):
    try:
        conn = await asyncpg.connect(
            user='db_admin',
            password='admin',
            database='db',
            host='127.0.0.1'
        )
        rows = await conn.fetch(
            "SELECT * FROM dialogs_history WHERE id_tread = $1",
            id_tread
        )
        await conn.close()

        # Преобразуем записи в строковый формат
        history = []
        for row in rows:
            history.append({"role": "user", "content": row['user_message']})
            history.append({"role": "assistant", "content": row['llm_response']})
        return history
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return str(e)
#проверить это всё
async def add_user_tread_id(id_user, id_tread):
    try:
        conn = await asyncpg.connect(
            user='db_admin',
            password='admin',
            database='db',
            host='127.0.0.1'
        )
        await conn.execute(
            """
            INSERT INTO users_treads (id_user, id_tread)
            VALUES ($1, $2)
            """,
            id_user,
            id_tread
        )
        await conn.close()
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return str(e)

async def fetch_user_tread_id(id_user):
    try:
        conn = await asyncpg.connect(
            user='db_admin',
            password='admin',
            database='db',
            host='127.0.0.1'
        )
        rows = await conn.fetch(
            "SELECT id_tread FROM users_treads WHERE id_user = $1",
            id_user
        )
        for row in rows:
            print(row) #особенно это!!!!!!!!!!!!!!!!!!!!!!!!!
        await conn.close()
        id_treads = [] 

        for row in rows:
            id_treads.append(row['id_tread'])
        return id_treads
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return str(e)

async def delete_user(id_user):
    try:
        id_treads = await fetch_user_tread_id(id_user)
        conn = await asyncpg.connect(
            user='db_admin',
            password='admin',
            database='db',
            host='127.0.0.1'
        )
        for id_tread in id_treads:
            await conn.execute(
                """
                DELETE FROM dialogs_history WHERE id_tread = $1
                """,
                id_tread
            )
        await conn.execute(
                """
                DELETE FROM users_treads WHERE id_user = $1
                """,
                id_user
            )
        await conn.close()
        return 0
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return 1

async def delete_tread(id_tread):
    try:
        conn = await asyncpg.connect(
            user='db_admin',
            password='admin',
            database='db',
            host='127.0.0.1'
        )
        
        await conn.execute(
            """
            DELETE FROM dialogs_history WHERE id_tread = $1
            """,
            id_tread
        )
        await conn.execute(
                """
                DELETE FROM users_treads WHERE id_tread = $1
                """,
                id_tread
            )
        await conn.close()
        return 0
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return 1
    
async def is_user_tread_in(id_user, id_tread):
    try:
        conn = await asyncpg.connect(
            user='db_admin',
            password='admin',
            database='db',
            host='127.0.0.1'
        )
        rows = await conn.fetch(
            """
            SELECT 
                CASE 
                    WHEN EXISTS (SELECT 1 FROM users_treads WHERE id_tread = $2 AND id_user = $1) 
                    THEN 0
                    ELSE 1 
                END AS result;

            """,
            id_user,
            id_tread
        )
        await conn.close()
        return(rows[0]['result'])
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return str(e)