from saver_bot.writer_bot_wizard import WriterBotWizard


def _get_wizard_for_writer(writer, *args, **kwargs):
    return WriterBotWizard(writer.properties.values(), writer.write, *args, **kwargs)


