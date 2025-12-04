import asyncio
import asyncpg
# Сначала добавим поле created_at в таблицу
#ALTER TABLE dialogs_history ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
from datetime import datetime
DATA_BASE = 'db2'
PASSWORD = 'admin'
USER = 'db_admin'
HOST = '127.0.0.1'




async def insert_data(id_tread, message, role, current_time = ''):
  if current_time:
    created_at = datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%S') #пример того, что придет: '2024-12-11T12:18:44'
  else:
    created_at = datetime.now()
  try:
    conn = await asyncpg.connect(
      user = USER,
      password = PASSWORD,
      database = DATA_BASE,
      host = HOST
    )
    await conn.execute(
      """
      INSERT INTO dialogs_history 
        (id_tread, content, role, created_at)
      VALUES 
        ($1, $2, $3, $4)
      """,
      id_tread,
      message,
      role,
      created_at
      
    )
    await conn.close()
  except Exception as e:
    print(f"Ошибка при записи данных: {e}")


async def fetch_history(id_tread):
  try:
    conn = await asyncpg.connect(
      user = USER,
      password = PASSWORD,
      database = DATA_BASE,
      host = HOST
    )
    rows = await conn.fetch(
      """
      SELECT * FROM dialogs_history 
      WHERE id_tread = $1 
      ORDER BY created_at
      """,
      id_tread
    )
    await conn.close()

    history = []
    for row in rows:
      history.append({
        "role": row['role'],
        "content": row['content'],
        
      })

    return history
  except Exception as e:
    print(f"Ошибка при чтении данных: {e}")
    return str(e)

async def add_user_tread_id(id_user, id_tread):
  try:
    conn = await asyncpg.connect(
      user = USER,
      password = PASSWORD,
      database = DATA_BASE,
      host = HOST
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
      user = USER,
      password = PASSWORD,
      database = DATA_BASE,
      host = HOST
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
      user = USER,
      password = 'admin',
      database = DATA_BASE,
      host = HOST
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
      user = USER,
      password = 'admin',
      database = DATA_BASE,
      host = HOST
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
      user = USER,
      password = 'admin',
      database = DATA_BASE,
      host = HOST
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
  ###
async def save_tread_picture(id_tread, picture):
    try:
        conn = await asyncpg.connect(
            user=USER,
            password=PASSWORD,
            database=DATA_BASE,
            host=HOST
        )
        await conn.execute(
            """
            INSERT INTO tread_picture (id_tread, picture)
            VALUES ($1, $2)
            """,
            id_tread,
            picture
        )
        await conn.close()
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return str(e)
    
async def get_pictures_by_tread(id_tread):
    try:
        conn = await asyncpg.connect(
            user=USER,
            password=PASSWORD,
            database=DATA_BASE,
            host=HOST
        )
        rows = await conn.fetch(
            "SELECT picture FROM tread_picture WHERE id_tread = $1",
            id_tread
        )
        await conn.close()
        pictures = [] 

        for row in rows:
            pictures.append(row['picture'])
        return pictures
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return str(e)

async def delet_pictures_from_table_by_tread(id_tread):
    try:
        conn = await asyncpg.connect(
            user=USER,
            password=PASSWORD,
            database=DATA_BASE,
            host=HOST
        )
        
        await conn.execute(
            """
            DELETE FROM tread_picture WHERE id_tread = $1
            """,
            id_tread
        )
        await conn.close()
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")