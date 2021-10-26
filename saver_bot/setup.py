from telegram.ext import CallbackContext

from saver_bot import user_state
from saver_bot.integrations.notion.writers import NotionBlockListWriter, NotionDatabaseWriter
from saver_bot.integrations.properties import StringProperty
from saver_bot.writer_bot_wizard import WriterBotWizard


def get_available_writers(context: CallbackContext):
    return {
        'Notion item list': NotionBlockListWriter,
        'Notion database': NotionDatabaseWriter,
    }


def get_writer_setup_wizard(context: CallbackContext, writer_name):
    writer_class = get_available_writers(context)[writer_name]
    properties = (
        StringProperty('name', 'Name'),
        *writer_class.required_properties,
    )
    return WriterBotWizard(properties, lambda params: add_writer(context, writer_name, params))


def add_writer(context: CallbackContext, writer_name, params):
    if user_state.AVAILABLE_WRITERS not in context.user_data:
        context.user_data[user_state.AVAILABLE_WRITERS] = {}

    context.user_data[user_state.AVAILABLE_WRITERS][params['name']] = [writer_name, params]
