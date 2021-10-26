import json
from collections import defaultdict
from typing import DefaultDict, Tuple, Optional, Dict

from redis import Redis
from telegram.ext import BasePersistence
from telegram.ext.utils.types import CD, UD, ConversationDict

_noop = lambda *a, **kw: None
_CHAT_HASH = 'CHAT_DATA'
_USER_HASH = 'USER_DATA'
_CONVERSATIONS_HASH = 'CONVERSATION_DATA'


class RedisPersistence(BasePersistence):
    def __init__(self, redis: Redis, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis
        self._chat_data = defaultdict(dict)
        self._user_data = defaultdict(dict)

    get_bot_data = _noop
    update_bot_data = _noop
    refresh_bot_data = _noop

    def get_chat_data(self) -> DefaultDict[int, CD]:
        self._chat_data = defaultdict(dict)
        self._chat_data.update({
            int(k): v
            for k, v in self._get_all_hash_keys(_CHAT_HASH).items()
        })
        return self._chat_data

    def get_conversations(self, name: str) -> ConversationDict:
        return {
            tuple(int(i) for i in k.split('/')): v
            for k, v in self._get_all_hash_keys(_CONVERSATIONS_HASH).items()
        }

    def get_user_data(self) -> DefaultDict[int, UD]:
        self._user_data = defaultdict(dict)
        self._user_data.update({
            int(k): v
            for k, v in self._get_all_hash_keys(_USER_HASH).items()
        })
        return self._user_data

    def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        pass

    def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        self._user_data[user_id] = self._get_hash_key(_USER_HASH, str(user_id))

    def update_chat_data(self, chat_id: int, data: CD) -> None:
        self._set_hash_key(_CHAT_HASH, str(chat_id), data)

    def update_conversation(self, name: str, key: Tuple[int, ...], new_state: Optional[object]) -> None:
        self._set_hash_key(_CONVERSATIONS_HASH, '/'.join(str(i) for i in key), new_state)

    def update_user_data(self, user_id: int, data: UD) -> None:
        self._set_hash_key(_USER_HASH, str(user_id), data)

    def _get_all_hash_keys(self, key: str):
        hash_dict = self.redis.hgetall(key)
        return {
            k: json.loads(v)
            for k, v in hash_dict.items()
        }

    def _get_hash_key(self, hash: str, key: str):
        str_data = self.redis.hget(hash, key)
        if str_data is None:
            return None
        return json.loads(str_data)

    def _set_hash_key(self, hash: str, key: str, data: Dict):
        str_data = json.dumps(data)
        self.redis.hset(hash, key, str_data)
