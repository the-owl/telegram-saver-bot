import functools
import typing

from telegram import Update
from telegram.ext import CallbackContext

from saver_bot import senders, user_state
from saver_bot.setup import get_available_writers
from saver_bot.dialog_state import DialogState
from saver_bot.config import get_available_wizards
from saver_bot.writer_bot_wizard import WriterBotWizard


def start(update: Update, context: CallbackContext) -> DialogState:
    senders.main_menu(update, context)
    return DialogState.MAIN_MENU


def handle_notion_token(update: Update, context: CallbackContext) -> DialogState:
    context.user_data[user_state.NOTION_ACCESS_TOKEN] = update.message.text
    senders.main_menu(update, context)
    return DialogState.MAIN_MENU


def setup_menu(update: Update, context: CallbackContext) -> DialogState:
    writers = get_available_writers(context)
    message = update.message.text

    context.user_data[user_state.SETUP_WRITER] = message
    wizard.initialize(update, context)

    return DialogState.INPUT


def with_wizard(fn):
    @functools.wraps(fn)
    def wrapper(update: Update, context: CallbackContext):
        writers = get_available_wizards(context)
        wizard = writers[context.user_data[user_state.WIZARD]]
        return fn(update, context, wizard)

    return wrapper


def main_menu(update: Update, context: CallbackContext) -> DialogState:
    message = update.message.text
    writers = get_available_wizards(context)
    try:
        wizard = writers[message]
    except KeyError:
        return DialogState.MAIN_MENU

    context.user_data[user_state.WIZARD] = message
    wizard.initialize(update, context)

    return DialogState.INPUT


@with_wizard
def handle_input(update: Update, context: CallbackContext, wizard: WriterBotWizard) -> typing.Optional[DialogState]:
    input_finished = wizard.handle_input(update, context)

    if input_finished:
        senders.saved(update)
        senders.main_menu(update, context)
        return DialogState.MAIN_MENU

    return None


@with_wizard
def handle_input_skip(update: Update, context: CallbackContext,
                      wizard: WriterBotWizard) -> typing.Optional[DialogState]:
    input_finished = wizard.handle_skip(update, context)

    if input_finished:
        senders.saved(update)
        senders.main_menu(update, context)
        return DialogState.MAIN_MENU

    return None
