import asyncpg
from django.conf import settings
from datetime import datetime

class Database:
    @staticmethod
    async def fetch_dialogs(start_date=None, end_date=None, id_tread=None):
        conn = await asyncpg.connect(settings.DATABASE_URL)
        try:
            query = """
                SELECT id_tread, COUNT(*) AS message_count, MAX(created_at) AS last_message_time
                FROM dialogs_history
                WHERE 1=1
            """
            params = []
            param_count = 1

            if id_tread:
                query += f" AND id_tread = ${param_count}"
                params.append(id_tread)
                param_count += 1

            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query += f" AND created_at >= ${param_count}"
                params.append(start_date)
                param_count += 1

            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query += f" AND created_at <= ${param_count}"
                params.append(end_date)
                param_count += 1

            # Сортировка по количеству сообщений (убывание), затем по последнему сообщению
            query += " GROUP BY id_tread ORDER BY message_count DESC, last_message_time DESC"

            result = await conn.fetch(query, *params)
            return [{"id_tread": row["id_tread"], "message_count": row["message_count"]} for row in result]
        finally:
            await conn.close()


    @staticmethod
    async def fetch_messages(id_tread, start_date=None, end_date=None):
        conn = await asyncpg.connect(settings.DATABASE_URL)
        try:
            query = """
                SELECT role, content, created_at 
                FROM dialogs_history 
                WHERE id_tread = $1
            """
            params = [id_tread]
            param_count = 2  # Начинаем с 2, так как id_tread уже занял $1

            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query += f" AND created_at >= ${param_count}"
                params.append(start_date)
                param_count += 1

            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query += f" AND created_at <= ${param_count}"
                params.append(end_date)
                param_count += 1
            print(start_date, end_date)
            query += " ORDER BY created_at"

            result = await conn.fetch(query, *params)
            return [{"role": row["role"], "text": row["content"], "created_at": row["created_at"]} for row in result]
        finally:
            await conn.close()

