import asyncio
from connect_to_db import delete_user
import json

with open("dialogs (2).json", 'r') as file:
    data = json.load(file)['girls'][0]['threads']
async def load(data):  
    users = []
    for record in data: 
        users.append(record['consumer_id'])
    for user in users:
        res = await delete_user(user)
        if not res:
            print('user is succsessfully deleted')
        else:
            print("Error")
asyncio.run(load(data))