# -*- coding: utf-8 -*-
import logging

from random import randint
from vk_api.vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

try:
    from settings import GROUP_ID, TOKEN
except ImportError:
    exit('DO cp settings.py.default settings.py and set TOKEN!!')

bot_logger = logging.getLogger("bot")

def loggers_configure():
    """
    Конфигурация логгеров
    :return: None
    """

    my_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M")

    file_handler = logging.FileHandler("bot.log", encoding="UTF-8")
    file_handler.setFormatter(my_formatter)

    bot_logger.addHandler(file_handler)
    bot_logger.setLevel("DEBUG")


class Bot:
    """
    Echo bot для вк
    Use Python 3.9 """
    def __init__(self, group_id, token):
        """
        :param group_id: айди группы вк
        :param token: секретный токен для работы с апи
        """
        self.group_id = group_id
        self.token = token
        self.vk_session = VkApi(token=self.token)
        self.longpoller = VkBotLongPoll(self.vk_session, self.group_id)
        self.vk_api = self.vk_session.get_api()

    def run(self):
        """
        Запуск бота
        :return: None
        """
        for event in self.longpoller.listen():
            bot_logger.debug("Получен эвент")
            try:
                self.on_event(event)
            except Exception:
                bot_logger.exception("Ошибка при запуске")

    def on_event(self, event):
        """
        Отправка сообщения идентичного полученному
        :param event: VkBotEventType
        :return: None
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            random_id = randint(0, 2 ** 10)
            message = event.object.message['text']
            peer_id = event.object.message['peer_id']
            self.vk_api.messages.send(random_id=random_id, peer_id=peer_id,
                                      message=message)
            bot_logger.info("Отправленно сообщение")



if __name__ == '__main__':
    loggers_configure()
    bot = Bot(group_id=GROUP_ID,
              token=TOKEN)
    bot.run()
