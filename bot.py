# -*- coding: utf-8 -*-
from random import randint

import vk_api
from vk_api import bot_longpoll

class Bot:

    def __init__(self, group_id, token):

        self.group_id = group_id
        self.token = token
        self.vk_session = vk_api.vk_api.VkApi(token=self.token)
        self.longpoller = vk_api.bot_longpoll.VkBotLongPoll(self.vk_session, self.group_id)
        self.vk_api = self.vk_session.get_api()


    def run(self):
        for event in self.longpoller.listen():
            try:
                self.on_event(event)
            except Exception as exc:
                print(exc)

    def on_event(self, event):
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            random_id = randint(0, 2 ** 10)
            peer_id = event.object.message['peer_id']
            self.vk_api.messages.send(random_id=random_id, peer_id=peer_id, message='dick')




if __name__ == '__main__':
    bot = Bot(group_id=205911168,
              token='d3e3dc20f6a2ee6d540489f5eba581e49ad7dcd4f54218eaa86119a96459e95852cb2517130d5714c1113')
    bot.run()