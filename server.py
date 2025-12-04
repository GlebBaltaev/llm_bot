# server.py
import asyncio
import uuid
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from ChatBot import *
from Dialog import *
from connect_to_db import *
from fastapi import Response
from datetime import datetime

dialogs = {}
chatbot = ChatBot(model_name='phi4:14b', model_url='http://localhost:11434/api/chat')
app = FastAPI()
#class ReqBody(BaseModel):
#    prompt: str
#    id_tread: str | None
#    id_user: str | None
##   event: str
class ReqBody(BaseModel):
    prompt: str
    id_tread: Optional[str] = ''  # Явно указываем None как значение по умолчанию
    id_user: Optional[str] = '123'
    event: str
async def logging(log_inf):
    formatted_string = ' '.join(f"{key}: {value};" for key, value in log_inf.items()) + "\n\n"
    with open('log.txt', 'a') as file:
        file.write(formatted_string)
    print("Данные записаны в файл.")
@app.post("/llm/")
async def request(body: ReqBody, request:Request):
    try:
        id_tread = body.id_tread or str(uuid.uuid4())
        id_user = body.id_user 
        user_message = body.prompt
        event = body.event
        print('id_tread = ', body.id_tread, 'id_user = ', id_user,event, user_message[:50])
        if event =='dialog_name':
            response = chatbot.get_name_of_dialog(dialogs[id_tread].get_history())
            return {'response': response['content'], 'id_tread': id_tread}          #отправляем название диалога, но сохранять в историю его не надо.
        elif event =='summarize':
            response = chatbot.get_name_of_dialog(dialogs[id_tread].get_history())
            return {'response': response['content'], 'id_tread': id_tread}          #отправляем краткое содержание.
        elif event =='delete_tread':                                                #наша задача удалить полученный тред из истории переписки
            res = await delete_tread(id_tread)
            if not res:
                print('tread is succsessfully deleted')
                Response(status_code=200)
            else:
                return Response(status_code=404)
        elif event =='delete_user':                                                  #наша задача удалить все треды этого пользователя в истории
            res = await delete_user(id_user)
            if not res:
                print('user is succsessfully deleted')
                return Response(status_code=200)
            else:
                return Response(status_code=404)
   
        #РАБОТАЕМ С АРХИВОМ, КЭШЕМ ИЛИ СОЗДАЕМ НОВЫЙ
         
        if (body.id_tread) and id_tread not in dialogs:                #у нас есть id_tread, но в кэше его, нет, поднимаем из архива
            h = await fetch_history(id_tread)
            print('Загружен из архива')
            print(*h)
            dialogs[id_tread] = Dialog()
            dialogs[id_tread].dialog = h
        elif id_tread not in dialogs:                                          #первый запрос, когда нет id_user, используем как системный для всего диалога. При этом у нас будет еще один - от чат бота
            print('Новый диалог')
            dialogs[id_tread] = Dialog(user_message)
            user_message = 'Начинай!'                                       #но чтобы бот начал общаться с нами, мы его тригернем
            await add_user_tread_id(id_user, id_tread)
            print("tread и user связаны")
        else:
            print('Нашли диалог в кэше')
        current_dialog = dialogs[id_tread]
        current_dialog.add_user_message(user_message)                     #сразу в историю добавляем сообщение пользователя, чтобы уже с учетом него получить ответ ллм
        history = current_dialog.get_history()                            #получаем историю
        
        response = chatbot.send_to_llm(history)                             #получаем ответ от ллм
        current_dialog.add_llm_message(response['content'])               #сохраняем в историю ответ ллм. надо бы проверить, чтобы там не сохранялись ошибки  сервера... НАДО ЭТО УЧЕСТЬ ПОТОМ.
        await insert_data(id_tread, user_message, response['content'], chatbot.model_name)        
        await logging({'user_mess': body.prompt, 'event': body.event, 'id_user': id_user, 'id_tread': id_tread, 'ip': request.client.host, 'datetime': datetime.now(), 'llm_res': response['content'][:100]})                                                                              
        return {'response': response['content'], 'id_tread': id_tread}        #Возвращаем ответ 
    except Exception as e:
        await logging({'error': e})
        return Response(status_code=500)


@app.get("/history/{id_tread}")
async def history(user_id: str):
    if user_id not in dialogs:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    return {"history": dialogs[user_id].get_history(), "user_id": user_id}