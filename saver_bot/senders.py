from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from saver_bot.config import get_available_wizards
from saver_bot.setup import get_available_writers
from saver_bot.keyboards import make_auto_reply_keyboard


def setup_menu(update: Update, context: CallbackContext):
    writers = get_available_writers(context)
    reply_markup = make_auto_reply_keyboard(writers.keys())
    update.message.reply_text('Select type of destination', reply_markup=reply_markup)


def main_menu(update: Update, context: CallbackContext):
    wizards = get_available_wizards(context)
    reply_markup = make_auto_reply_keyboard(wizards.keys())
    update.message.reply_text('What do you want to dump into Notion?', reply_markup=reply_markup)


def request_notion_token(update: Update):
    update.message.reply_text('👋 Hi! To get started, send me your Notion access token. ' +
                              'To obtain one, create a new integration here: https://www.notion.so/my-integrations',
                              reply_markup=ReplyKeyboardRemove())


def request_todo(update: Update):
    update.message.reply_text('What should be done?')


def request_thought(update: Update):
    update.message.reply_text('What\'s on your mind?')


def request_book(update: Update):
    update.message.reply_text('What\'s the name of the book?')


def bad_reply(update: Update):
    update.message.reply_text('Please select one of the options, I\'m not yet smart enough to understand words :(')


def saved(update: Update):
    update.message.reply_text('Saved!')
