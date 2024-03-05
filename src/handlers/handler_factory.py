import importlib
import pathlib
from handlers.abstract_handler import AbstractHandler

class HandlerFactory:
    _handlers = {}

    @classmethod
    def discover_handlers(cls, root_path='./src/handlers'):
        # Convert to Path object for easier manipulation
        root = pathlib.Path(root_path)
        
        for path in root.rglob('*.py'):  # Recursively go through all .py files
            # Skip __init__.py files to avoid imports of package initializers
            if path.name == '__init__.py':
                continue
            

            # Generate a module path for importlib
            relative_path = path.relative_to(root.parent)
            module_path = '.'.join(relative_path.with_suffix('').parts)
            
            # Dynamically import the module
            module = importlib.import_module(module_path)

            # Inspect all attributes of the module to find handler classes
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, AbstractHandler) and attribute is not AbstractHandler:
                    # Store the handler class for later instantiation
                    handler_name = attribute.__name__
                    cls._handlers[handler_name] = attribute

    @classmethod
    def get_handler(cls, handler_type):
        # Ensure handlers are discovered before attempting to get one
        if not cls._handlers:  # Discover handlers if not already done
            cls.discover_handlers()
        handler_class = cls._handlers.get(handler_type)
        if handler_class:
            return handler_class()  # Instantiate the handler
        else:
            raise ValueError(f"Handler not found for type: {handler_type}")