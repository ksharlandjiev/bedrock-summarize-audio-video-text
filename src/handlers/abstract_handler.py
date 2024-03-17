from __future__ import annotations
from abc import abstractmethod
from typing import Any
from handlers.handler import Handler
class AbstractHandler(Handler):
    """
    The default chaining behavior can be implemented inside a base handler
    class.
    """

    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a
        # convenient way like this:
        # local_file_handler.set_next(prompt_handler).set_next(summarization_handler)
        return handler

    @abstractmethod
    def handle(self, request: dict) -> dict:
        if self._next_handler:
            return self._next_handler.handle(request)

        return request