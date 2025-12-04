import re
#процедура удаляет размышления deepSeek,  чтобы они не сохранялись в истории.


class Dialog():
    count_of_users = 1
    def __init__(self,start_prompt=''):
        self.user_id = Dialog.count_of_users
        Dialog.count_of_users += 1
        self.dialog = [{"role": "system", "content": start_prompt}] if start_prompt else []
        self.saved = 0

    def add_user_message(self, user_message):
        self.dialog.append({"role": "user", "content": user_message})
        self.saved = 0
    def add_llm_message(self, llm_message):
        self.dialog.append({"role": "assistant", "content": llm_message}) #не уверен, но возможно у дипсика надо удалить его размышления
        self.saved = 1
    #def add_message(self, user_message, llm_response):
    #    self.dialog += 'Сообщение пользователя: ' + user_message + '\n' +  'Сообщение модели: ' + llm_response
    #    self.saved = 1
    def get_history(self):
        return self.dialog
    