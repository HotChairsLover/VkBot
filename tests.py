import unittest
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot


class MyTestCase(unittest.TestCase):
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

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)
        send_mock = Mock()
        with patch('bot.VkApi'):
            with patch('bot.VkBotLongPoll'):
                bot = Bot('', '')
                bot.vk_api = Mock()
                bot.vk_api.messages.send = send_mock

                bot.on_event(event)

        send_mock.assert_called_once_with(
            message=self.RAW_EVENT['object']['message']['text'],
            random_id=ANY,
            peer_id=self.RAW_EVENT['object']['message']['peer_id']
        )


if __name__ == '__main__':
    unittest.main()
