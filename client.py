# client.py
import requests
user_id = None
while True:
    i = input("Ваше сообщение: ")
    if not i:
        break
    data = {"user_id": user_id, "query": i, "event": "start" if user_id is None else 'message'}
    r = requests.post("http://localhost:8000/llm/", json=data) 
    if r.status_code == 200:
        print("Бот:", r.json()["response"])
        if user_id is None:
            user_id = r.json()["user_id"]
    else:
        print("Ошибка при обращении к серверу")
r = requests.get(f"http://localhost:8000/history/{user_id}")
print('\n\n' + r.json()["user_id"] + '\n\n' + r.json()["history"])