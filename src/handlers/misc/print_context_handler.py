from typing import Any

from handlers.abstract_handler import AbstractHandler

class PrintContextHandler(AbstractHandler):
    """
    Simple handler that only prints the request context.
    """
    def handle(self, request: dict) -> dict:
        print("============================================================")
        print(request)
        print("============================================================")

        return super().handle(request)