import yaml

from saver_bot.integrations.notion import NotionProvider
from saver_bot.writer_bot_wizard import WizardPropertySettings, WriterBotWizard

KNOWN_PROVIDERS = (
    NotionProvider,
)


_wizards = None


def init_from_config_file(config_filename: str):
    global _wizards

    with open(config_filename, 'r') as file:
        data = yaml.safe_load(file)

    providers = _extract_config_providers(data)
    writers, writers_provider = _extract_available_writers(providers)
    _wizards = _extract_available_wizards(data['wizards'], writers, writers_provider)


def get_available_wizards(context):
    return _wizards


def _extract_config_providers(config: dict):
    providers = {}

    for name, settings in config['providers'].items():
        provider_class = next(c for c in KNOWN_PROVIDERS if c.__name__ == name)
        providers[name] = provider_class(**settings)

    return providers


def _extract_available_writers(providers: dict):
    writers = {}
    writers_provider = {}

    for provider in providers.values():
        for writer in provider.get_available_writers():
            writers[writer.__name__] = writer
            writers_provider[writer.__name__] = provider

    return writers, writers_provider


def _extract_available_wizards(wizard_settings: dict, available_writers: dict, writers_provider: dict):
    wizards = {}

    for name, settings in wizard_settings.items():
        writer_class = available_writers[settings['writer']]
        provider = writers_provider[settings['writer']]
        writer = writer_class(
            **provider.get_writer_params(),
            **settings['writer_params'],
        )

        properties = {}
        for property_name, property_settings in settings.get('property_settings', {}).items():
            properties[property_name] = WizardPropertySettings(**property_settings)

        property_order = settings.get('property_order')
        wizard = WriterBotWizard(writer.properties.values(), writer.write, property_order, properties)
        wizards[name] = wizard

    return wizards
