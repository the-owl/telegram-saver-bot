from typing import Sequence, Optional, Any, Dict, Callable

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from saver_bot import user_state
from saver_bot.integrations.properties import Property, SelectProperty, StringProperty


class WizardPropertySettings:
    def __init__(self, skippable: bool = False, default: Optional[Any] = None):
        self.skippable = skippable
        self.default = default


DEFAULT_FIELD_SETTINGS = WizardPropertySettings()


class WriterBotWizard:
    def __init__(self,
                 properties: Sequence[Property],
                 finish_callback: Callable,
                 property_order: Optional[Sequence[str]] = None,
                 field_settings: Optional[Dict[str, WizardPropertySettings]] = None):
        self._properties = {p.name: p for p in properties}
        self._finish_callback = finish_callback
        self._property_order = property_order
        self._field_settings = {} if field_settings is None else field_settings

    @property
    def defaults(self):
        return {
            k: f.default
            for k, f in self._field_settings.items()
        }

    def get_current_property(self, context: CallbackContext):
        prop_name = context.user_data[user_state.WIZARD_CURRENT_PROPERTY]
        return self._properties[prop_name]

    def get_field_settings(self, name: str):
        return self._field_settings.get(name, DEFAULT_FIELD_SETTINGS)

    def handle_input(self, update: Update, context: CallbackContext):
        current_property = self.get_current_property(context)
        serializer = self._get_property_serializer(current_property)

        raw_value = update.message.text

        serialized_value = serializer(raw_value)

        context.user_data[user_state.DRAFT][current_property.name] = serialized_value
        return self.next_property_or_finish(update, context)

    def handle_skip(self, update, context):
        return self.next_property_or_finish(update, context)

    def next_property_or_finish(self, update: Update, context: CallbackContext):
        current_property = self.get_current_property(context)
        current_property_index = self.property_order.index(current_property.name) + 1

        if current_property_index == len(self.property_order):
            item = {
                **self.defaults,
                **context.user_data[user_state.DRAFT],
            }
            context.job_queue.run_once(lambda c: self._finish_callback(item), 0)
            return True

        next_property_name = self.property_order[current_property_index]

        self.send_prompt(update, next_property_name)
        context.user_data[user_state.WIZARD_CURRENT_PROPERTY] = next_property_name

        return False

    def initialize(self, update: Update, context: CallbackContext):
        context.user_data[user_state.WIZARD_CURRENT_PROPERTY] = self.property_order[0]
        context.user_data[user_state.DRAFT] = {**self.defaults}
        self.send_prompt(update, self.property_order[0])

    @property
    def property_order(self):
        if self._property_order:
            return self._property_order

        self._property_order = [p.name for p in self._properties.values()]
        return self._property_order

    def send_prompt(self, update: Update, current_property_name: str):
        property = self._properties[current_property_name]
        sender = _PROPERTY_SENDERS[property.type]
        settings = self.get_field_settings(current_property_name)
        sender(update, property, settings)

    def _get_property_serializer(self, property):
        return _PROPERTY_SERIALIZERS[property.type]


def _prompt_plaintext(update: Update, property: Property, settings: WizardPropertySettings):
    skip_msg = ' (or /skip)' if settings.skippable else ''
    update.message.reply_text(f'Enter {property.name.lower()}{skip_msg}')


def _prompt_select(update: Update, property: SelectProperty, settings: WizardPropertySettings):
    reply_keyboard = [[
        o.name for o in property.options
    ]]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True,
    )
    skip_msg = ' (or /skip)' if settings.skippable else ''
    update.message.reply_text(f'Enter {property.name.lower()}{skip_msg}', reply_markup=reply_markup)


def _noop_serializer(value):
    return value


_PROPERTY_SENDERS = {
    StringProperty.type: _prompt_plaintext,
    SelectProperty.type: _prompt_select,
}

_PROPERTY_SERIALIZERS = {
    StringProperty.type: _noop_serializer,
    SelectProperty.type: _noop_serializer,
}
