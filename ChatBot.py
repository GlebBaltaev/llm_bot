#ИНСТРУКЦИЯ ПО API OLLAMA https://github.com/ollama/ollama/blob/main/docs/api.md
import requests
import json
import re

def extract_visible_text(text):
    #функция удаляет всё, что в тегах <think>
    pattern = r'<think>.*?</think>'
    return re.sub(pattern, '', text, flags=re.DOTALL)
    
def is_model_loaded(model, model_url):
    #получаем список  загруженных моделей на GPU и смотрим есть ли там наша
    test_url = model_url.replace('chat','ps')
    try:
        response = requests.get(test_url)
        loaded_models = [k['name'] for k in response.json().get("models", [])]
        print(loaded_models)
        return model in loaded_models
    except requests.exceptions.RequestException:
        return False
    
def load_model_in_gpu(model,model_url):
    data = {"model": model, "options":{"keep_alive":-1}}
    print('...загружаем в GPU...', model)
    r = requests.post(
                model_url,
                json=data,
                stream=False
            )
    
def ping_url(model, model_url, default_model, default_model_url):
    test_url = model_url.replace('chat','ps')
    print(test_url)
    try:
        response = requests.get(test_url, timeout=5)
        loaded_models = [k['name'] for k in response.json().get("models", [])]
        print('До', loaded_models, "\n" )
        if model not in loaded_models:
            load_model_in_gpu(model, model_url)
        response = requests.get(test_url)
        loaded_models = [k['name'] for k in response.json().get("models", [])]
        print('После', loaded_models, "\n" )
        return 0
    except requests.exceptions.ConnectionError as e:
        is_model_loaded(default_model, default_model_url)
        if not is_model_loaded(default_model, default_model_url):
            load_model_in_gpu(default_model, default_model_url)
        return 1
    except requests.exceptions.Timeout:
        print("Ошибка: превышено время ожидания (Timeout)")
        return 2
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return 2

class ChatBot():
    def __init__(self, model_name='deepseek-r1:14b', model_url='http://localhost:11434/api/chat', system_prompt='Пиши на русском', list_dialog=None, temperatura = 0.7, clear_think = True):
        #temperatura - задаем температуру в модели
        #clear_think - deepseek - на выходе дает рассуждение в тегах <think> </think>. Если True - то эти рассуждения из ответов будут удаляться
        self.model_name = model_name
        self.temperatura = temperatura
        self.model_url = model_url
        self.clear_think = clear_think
        res = ping_url(model_name, model_url, 'deepseek-r1:14b', 'http://localhost:11434/api/chat')
        if res:
            self.model_name = 'deepseek-r1:14b'
            self.model_url = 'http://localhost:11434/api/chat'
        self.system_prompt = [{"role": "system", "content": system_prompt}]
        self.list_dialog = list_dialog if list_dialog is not None else {}
        print(self.model_name, self.model_url)
    def send_to_llm(self, message):
        full_message = self.system_prompt + message
        data = {"model": self.model_name, "messages": full_message, "stream": False, "options":{"temperature":self.temperatura}}
        try:
            r = requests.post(
                self.model_url,
                json=data,
                stream=False
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f'Ошибка HTTP: {err}')
        except requests.exceptions.RequestException as err:
            print(f'Ошибка запроса: {err}')
        response_data = r.json()    
        if "error" in response_data:
            final_message = {"role": "assistant", "content": 'Похоже сервак занят. Надо подождать'}
            return final_message
        final_message = response_data.get("message")
        
        if self.clear_think: #проверяем надо ли чистить размышления
            final_message['content'] = extract_visible_text(final_message['content'])
        return final_message

    def summarize_dialog(self, dialog):    #краткое содержание диалога
        temp_task = [{"role": "user", "content": "Напиши краткое содержание диалога. 1-2 предложения. Ответь на русском"}]
        return self.send_to_llm(dialog + temp_task)
    
    def get_name_of_dialog(self, dialog):  #придумаем  небольшое название диалога
        temp_task = [{"role": "user", "content": "Придумай одно название к этому разговору,о чем мы с тобой общались, чтобы я мог сохранить диалог под этим названием, а потов вспонить и найти. Короткое название: 3-5 слов. Пиши только название. Ответь на русском"}]
        return self.send_to_llm(dialog + temp_task)
    
        
        return sys_prompt
    def open_dialog(self, user_id):
        return self.list_dialog[user_id]
    
    def save_dialog(self, dialog):
        pass

    def remove_from_cache(self, user_id):
        if user_id in self.list_dialog:
            del self.list_dialog[user_id]

    def flush_cache(self):
        pass


