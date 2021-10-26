from notion_client import Client

from saver_bot.integrations.notion.writers import NotionDatabaseWriter, NotionBlockListWriter


class NotionProvider:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.client = Client(auth=access_token)

    def get_available_writers(self):
        return NotionDatabaseWriter, NotionBlockListWriter

    def get_writer_params(self):
        return {
            'client': self.client,
        }

