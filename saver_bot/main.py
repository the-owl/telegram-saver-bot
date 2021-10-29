import logging
import os

from redis import Redis
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from saver_bot import handlers, config
from saver_bot.dialog_state import DialogState
from saver_bot.persistence import RedisPersistence

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    config_filename = os.environ.get('BOT_CONFIG', 'config.yaml')
    redis_url = os.environ.get('REDIS_CONNECTION_STRING', 'redis://localhost:6379/0')

    config_data = config.init_from_config_file(config_filename)
    telegram_token = config_data.bot_access_token

    redis = Redis.from_url(redis_url, decode_responses=True)
    updater = Updater(telegram_token, persistence=RedisPersistence(redis, store_bot_data=False, store_user_data=True))

    dispatcher = updater.dispatcher

    root_conv_handler = ConversationHandler(
        name='root_conversation',
        persistent=True,
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            DialogState.REQUEST_NOTION_TOKEN: [MessageHandler(Filters.text & ~Filters.command, handlers.handle_notion_token)],
            DialogState.SETUP_MENU: [MessageHandler(Filters.text & ~Filters.command, handlers.setup_menu)],
            DialogState.MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, handlers.main_menu)],
            DialogState.INPUT: [
                CommandHandler('skip', handlers.handle_input_skip),
                MessageHandler(Filters.text & ~Filters.command, handlers.handle_input),
            ],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(root_conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
