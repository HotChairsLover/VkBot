# -*- coding: utf-8 -*-
import logging
from random import randint

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.vk_api import VkApi

import handlers
import settings

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


class UserState:
    """Состояние пользователя внутри сценария."""

    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


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
        self.user_states = dict()  # user_id -> UserState

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
        if event.type != VkBotEventType.MESSAGE_NEW:
            bot_logger.info(f'мы пока не умеем обрабатывать событие такого типа {event.type}')
            return

        user_id = event.object.message['peer_id']
        text = event.object.message['text']

        if user_id in self.user_states:
            text_to_send = self.continue_scenatio(user_id=user_id, text=text)
        else:
            for intent in settings.INTENTS:
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER

        self.vk_api.messages.send(
            random_id=randint(0, 2 ** 10),
            peer_id=user_id,
            message=text_to_send,
        )

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenatio(self, user_id, text):
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                self.user_states.pop(user_id)
        else:
            text_to_send = step['failure_text'].format(**state.context)

        return text_to_send


if __name__ == '__main__':
    loggers_configure()
    bot = Bot(group_id=GROUP_ID,
              token=TOKEN)
    bot.run()
