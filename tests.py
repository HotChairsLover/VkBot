import unittest
from copy import deepcopy
from unittest.mock import patch, Mock

from vk_api.bot_longpoll import VkBotMessageEvent

import settings
from bot import Bot


class MyTestCase(unittest.TestCase):
    INPUTS = [
        'Привет',
        'А когда?',
        "Где будет конференция?",
        "Зарегистрируй меня",
        "Вениамин",
        "Мой адрес email@email",
        "email@email.ru"
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='email@email.ru')
    ]
    RAW_EVENT = {
        'type': 'message_new',
        'object': {
            'message': {'date': 1626900379, 'from_id': 233676259, 'id': 130, 'out': 0,
                        'peer_id': 233676259, 'text': 'УЫУЫА', 'conversation_message_id': 126,
                        'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [],
                        'is_hidden': False},
            'client_info': {'button_actions':
                                ['text', 'vkpay', 'open_app', 'location',
                                 'open_link', 'callback', 'intent_subscribe', 'intent_unsubscribe'],
                            'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}},
        'group_id': 205911168,
        'event_id': '01c602015b6e79f75e40845dd49937bc52c575d8'}

    def test_run(self):
        count = 5
        obj = {}
        event = [obj] * count  # [obj, obj, ...]
        long_poller_mock = Mock(return_value=event)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('bot.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_called_with(obj)
                assert bot.on_event.call_count == count

    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot("", "")
            bot.vk_api = api_mock
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS


if __name__ == '__main__':
    unittest.main()
