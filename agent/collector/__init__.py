"""Event collectors."""

from collector.windows import SimulatedEventReader, WindowsEventReader, build_reader

__all__ = ["SimulatedEventReader", "WindowsEventReader", "build_reader"]
