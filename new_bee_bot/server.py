# -*- coding: utf-8 -*-
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
import os

#ВРЕМЕННАЯ МЕРА. СОХРАНЯЕМ ДИАЛОГИ В ЭТОТ ПУТЬ в ФАЙЛЫ С РАСШИРЕНИЕМ TXT КАЖДЫЙ ФАЙЛ _ ЭТО ID TREAD
PATH_FOR_SAVE = 'save_dialogs'
if not os.path.exists(PATH_FOR_SAVE):
    os.makedirs(PATH_FOR_SAVE)

# def history_slice(history, id):
    # copied_list = history.copy()
    # tokens = dialogs_tokens.get(id, 0)
    # if tokens < 3500:
        # return history
    #а вот теперь надо обрезать историю так, чтобы было моменьше токенов


def quick_save(id_tread,txt):
    file_name = os.path.join(PATH_FOR_SAVE,id_tread+'.txt')
    with open(file_name, 'a', encoding='utf8') as f:
            f.write(f'{txt} ###{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')   #в конец строкеи запишем дату и время, чтобы потом можно было посмотреть были ли перерывы в диалоге.



dialogs = {}
dialogs_tokens ={} #токенов в текущем диалоге

chatbot = ChatBot(model_name='llama3.1:70b-instruct-q8_0', model_url='http://81.94.150.50:11435/api/chat', temperatura =0.05)
#chatbot = ChatBot(model_name='phi4:14b', model_url='http://176.99.135.8:11434/api/chat', temperatura =0.05) #яна

#chatbot = ChatBot(model_name='llama3.3:70b-instruct-q8_0', model_url='http://176.99.135.8:11434/api/chat', temperatura =0.01)
#chatbot = ChatBot(model_name='llama3.3:70b-instruct-q6_K', model_url='http://176.99.135.8:11434/api/chat', temperatura =0.01)


app = FastAPI()

class ReqBody(BaseModel):
    prompt: str
    id_tread: Optional[str] = ''  # Явно указываем None как значение по умолчанию
    id_user: Optional[str] = '123'
    event: str
    time_stamp: Optional[str] = ''
    allow_incoming_media: int = 1

    
async def logging(log_inf):
    formatted_string = ' '.join(f"{key}: {value};" for key, value in log_inf.items()) + "\n\n"
    with open('log.txt', 'a') as file:
        file.write(formatted_string)
    #print("Данные записаны в файл.")

@app.post("/mm/")
@app.post("/mm")
async def request(body: ReqBody, request:Request):
    try:
        id_tread = body.id_tread or str(uuid.uuid4())
        id_user = body.id_user 
        user_message = body.prompt
        event = body.event
        allow_incoming_media = body.allow_incoming_media
        print(f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} Вход.обращение: id_tread={body.id_tread} event: {event}, {user_message[:10].replace("\n","")}')
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
        elif event == 'insert_chater':    #надо в историю вставить это сообщение, как от имени чатера
            time_stamp = body.time_stamp
            await insert_data(id_tread, user_message, 'assistant',time_stamp)
            dialogs.pop(id_tread,None)  #удаляем из кэша
            return Response(status_code=200)
        elif event == 'insert_user':
            time_stamp = body.time_stamp
            await insert_data(id_tread, user_message, 'user', time_stamp)
            dialogs.pop(id_tread,None) #удаляем из кэша
            return Response(status_code=200)
            
            
        #РАБОТАЕМ С АРХИВОМ, КЭШЕМ ИЛИ СОЗДАЕМ НОВЫЙ
         
        if (body.id_tread) and id_tread not in dialogs:                #у нас есть id_tread, но в кэше его, нет, поднимаем из архива
            h = await fetch_history(id_tread)
            #print('Загружен из архива',h)
            #return ''
            dialogs[id_tread] = Dialog()
            #print('Системный',len(dialogs[id_tread].dialog))
            #print('История',len(h))
            
            dialogs[id_tread].dialog.extend(h)
            #print('Стало',len(dialogs[id_tread].dialog))
            
        elif id_tread not in dialogs:                                          #первый запрос, когда нет id_user, используем как системный для всего диалога. При этом у нас будет еще один - от чат бота
            print('Новый диалог')
            dialogs[id_tread] = Dialog(user_message)
            user_message = 'приветствуй'                                       #но чтобы бот начал общаться с нами, мы его тригернем
            await add_user_tread_id(id_user, id_tread)
        else:
            print('Нашли диалог в кэше')
        current_dialog = dialogs[id_tread]
        current_dialog.add_user_message(user_message)                     #сразу в историю добавляем сообщение пользователя, чтобы уже с учетом него получить ответ ллм
        await insert_data(id_tread, user_message, 'user')
        quick_save(id_tread,'USER: '+user_message)                           #ЭТО ВРЕМЕННАЯ ПРОЦЕДЦРА СОХРАНЕНИЯ ИСТОРИИ В ФАЙЛЫ БЕЗ SQL. НУЖНО, ЧТОБЫ МОЖНО БЫЛО БЫСТРО НАЙТИ ДИАЛОГ      
        history = current_dialog.get_history()                            #получаем историю
       
        #history = history_slice(history,id_tread) #пытаемся сохранить историю
        
        response = await chatbot.send_to_llm(history, id_tread, allow_incoming_media)                             #получаем ответ от ллм
        
        file = response["file_response"] if "file_response" in response else None
        if file: print(file[:10])
        current_dialog.add_llm_message(response['content'])               #сохраняем в историю  ответ ллм. надо бы проверить, чтобы там не сохранялись ошибки  сервера... НАДО ЭТО УЧЕСТЬ ПОТОМ.
        #dialogs_tokens['id_tread'] = tokens
        
        quick_save(id_tread,'МИРЕЛЬ: '+response['content'])                #ЭТО ВРЕМЕННАЯ ПРОЦЕДЦРА СОХРАНЕНИЯ ИСТОРИИ В ФАЙЛЫ БЕЗ SQL. НУЖНО, ЧТОБЫ МОЖНО БЫЛО БЫСТРО НАЙТИ ДИАЛОГ
        await insert_data(id_tread, response['content'], 'assistant')        
        return {'response': response['content'], 'id_tread': id_tread, "file": file}        #Возвращаем ответ 
    except Exception as e:
        await logging({'error': e})
        return Response(status_code=500)


@app.get("/history/{id_tread}")
async def history(user_id: str):
    if user_id not in dialogs:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    return {"history": dialogs[user_id].get_history(), "user_id": user_id}