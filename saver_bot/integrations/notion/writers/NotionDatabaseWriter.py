from box import Box
from notion_client import Client

from saver_bot.integrations.properties import SelectProperty, StringProperty, BooleanProperty


class NotionDatabaseWriter:
    _metadata_cache = {}
    required_properties = [
        StringProperty('database_id', 'Database ID'),
    ]

    def __init__(self, client: Client, database_id: str):
        self.client = client
        self.database_id = database_id

    @property
    def notion_properties(self):
        metadata = self._metadata_cache.get(self.database_id)
        if metadata is None:
            metadata = Box(self.client.databases.retrieve(self.database_id))
            self._metadata_cache[self.database_id] = metadata
        return metadata['properties']

    @property
    def properties(self):
        properties = {}

        for prop in self.notion_properties.values():
            if prop.type == 'select':
                p = SelectProperty(prop.name, [SelectProperty.Option(o.name) for o in prop.select.options])
            elif prop.type in ('rich_text', 'title', 'url'):
                p = StringProperty(prop.name)
            elif prop.type == 'checkbox':
                p = BooleanProperty(prop.name)
            else:
                print(f'WARNING: unsupported property type: {prop.type}')
                continue

            properties[prop.name] = p

        return properties

    def write(self, item: dict):
        properties = {}

        for property in self.notion_properties.values():
            if item.get(property.name) is None:
                continue

            serializer = get_property_serializer(property)
            value = serializer.get_notion_value(item[property.name])
            properties[property.name] = value

        self.client.pages.create(properties=properties, parent={'database_id': self.database_id})


class TitleSerializer:
    def get_notion_value(self, source_value: str):
        return Box({
            'type': 'title',
            'title': [
                {
                    'text': {'content': source_value},
                },
            ],
        })


class RichTextSerializer:
    def get_notion_value(self, source_value: str):
        return Box({
            'type': 'rich_text',
            'rich_text': [
                {
                    'type': 'text',
                    'text': {'content': source_value},
                },
            ],
        })


class SelectSerializer:
    def __init__(self, options):
        self.options = options

    def get_notion_value(self, source_value: str):
        return Box({
            'type': 'select',
            'select': {
                'name': source_value,
            },
        })


class CheckboxSerializer:
    def get_notion_value(self, source_value: bool):
        return Box({
            'type': 'checkbox',
            'checkbox': source_value,
        })


class UnknownPropertyType(Exception):
    pass


def get_property_serializer(property: Box):
    property_type = property.type

    if property_type == 'rich_text':
        return RichTextSerializer()
    if property_type == 'select':
        return SelectSerializer(property.select.options)
    if property_type == 'title':
        return TitleSerializer()
    if property_type == 'checkbox':
        return CheckboxSerializer()

    raise UnknownPropertyType(f'type = {property_type}')
