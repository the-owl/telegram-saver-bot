import typing


class Property:
    def __init__(self, name: str, display_name: typing.Optional[str] = None):
        self.name = name
        self.display_name = name if display_name is None else display_name


class StringProperty(Property):
    type = 'string'


class BooleanProperty(Property):
    type = 'boolean'


class SelectProperty(Property):
    class Option:
        def __init__(self, value: str, name: typing.Optional[str] = None):
            self.name = value if name is None else name
            self.value = value

    type = 'select'

    def __init__(self, name: str, options: typing.Sequence[Option], display_name: typing.Optional[str] = None):
        super().__init__(name, display_name)
        self.options = options
