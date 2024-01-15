# -*- coding: utf-8 -*-
"""To have all logger creation in one place."""

import logging

from colorama import Fore, Back, Style


def get_astar_logger() -> logging.Logger:
    """Get a logger with name "astar"."""
    return logging.getLogger("astar")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with given name as a child of the "astar" logger."""
    return get_astar_logger().getChild(name)


class ColoredFormatter(logging.Formatter):
    """Formats colored logging output to console."""

    colors = {
        logging.DEBUG: Fore.CYAN,  # Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.MAGENTA,  # Fore.CYAN,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.YELLOW + Back.RED
    }

    def __init__(self, show_name: bool = True, **kwargs):
        self._show_name = show_name
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"<{self.__class__.__name__}>"

    def _get_fmt(self, level: int) -> str:
        log_fmt = [
            self.colors.get(level),
            Style.BRIGHT * (level >= logging.ERROR),
            "%(name)s - " * self._show_name,
            "%(levelname)s: " * (level >= logging.WARNING),
            "%(message)s" + Style.RESET_ALL,
        ]
        return "".join(log_fmt)

    def formatMessage(self, record):
        """Override `logging.Formatter.formatMessage()`."""
        log_fmt = self._get_fmt(record.levelno)
        return log_fmt % record.__dict__

    # Could maybe add bug_report here somehow?
    # def formatException(self, ei):
    #     return super().formatException(ei) + "\n\nextra text"
