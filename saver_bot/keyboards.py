from typing import Sequence

from telegram import ReplyKeyboardMarkup


MAX_ITEMS_IN_ROW = 3


def make_auto_reply_keyboard(items: Sequence[str]):
    reply_keyboard = [[]]
    for item in items:
        reply_keyboard[-1].append(item)
        if len(reply_keyboard[-1]) == MAX_ITEMS_IN_ROW:
            reply_keyboard.append([])
    return ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True,
    )
