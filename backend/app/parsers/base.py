"""Parser interface. New log formats implement this contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedEvent:
    event_id: int | None = None
    provider: str | None = None
    computer: str | None = None
    time_created: str | None = None
    user: str | None = None
    event_data: dict = field(default_factory=dict)
    raw: str | None = None


class BaseParser(ABC):
    format_name: str = "base"
    version: str = "1.0"

    @abstractmethod
    def parse(self, payload: str | dict) -> ParsedEvent | None:
        raise NotImplementedError
