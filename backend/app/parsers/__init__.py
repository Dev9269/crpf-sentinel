"""Parser registry — add new formats by implementing BaseParser."""

from app.parsers.base import BaseParser
from app.parsers.windows import WindowsEventParser


class ParserRegistry:
    _parsers: dict[str, BaseParser] = {}

    @classmethod
    def register(cls, parser: BaseParser) -> None:
        cls._parsers[parser.format_name] = parser

    @classmethod
    def get(cls, format_name: str) -> BaseParser:
        parser = cls._parsers.get(format_name)
        if parser is None:
            raise ValueError(f"Unsupported log format: {format_name}")
        return parser

    @classmethod
    def all(cls) -> list[str]:
        return list(cls._parsers.keys())


ParserRegistry.register(WindowsEventParser())
