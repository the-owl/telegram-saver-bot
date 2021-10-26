from enum import Enum

from notion_client import Client

from saver_bot.integrations.properties import StringProperty, SelectProperty


class NotionBlockListWriter:
    class BlockType(Enum):
        TO_DO = 'to_do'
        BULLETED_LIST_ITEM = 'bulleted_list_item'

    required_properties = [
        StringProperty('page_id', 'Page ID'),
        SelectProperty('block_type', display_name='Block type', options=[
            SelectProperty.Option(BlockType.TO_DO.value, 'To-Do'),
            SelectProperty.Option(BlockType.BULLETED_LIST_ITEM.value, 'Bullet list'),
        ]),
    ]

    def __init__(self, client: Client, page_id: str, block_type: str):
        self.page_id = page_id
        self.client = client
        self.block_type = block_type

    @property
    def properties(self):
        return {
            'Name': StringProperty('Name'),
        }

    def write(self, item: dict):
        self.client.blocks.children.append(self.page_id, children=[
            {
                'object': 'block',
                'type': self.block_type,
                self.block_type: {
                    'text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': item['Name'],
                            },
                        },
                    ],
                },
            },
        ])