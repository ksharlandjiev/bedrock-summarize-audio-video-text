import ast
import pathlib
import importlib

from handlers.abstract_handler import AbstractHandler

class HandlerFactory:
    _handlers = {}
    _handler_paths = {}

    @classmethod
    def discover_handlers(cls, root_path='./src/handlers'):
        root = pathlib.Path(root_path)

        for path in root.rglob('*.py'):
            if path.name == '__init__.py':
                continue

            # Read the content of the Python file
            with open(path, 'r') as file:
                node = ast.parse(file.read(), filename=path.name)

            # Traverse the AST to find class definitions that extend AbstractHandler
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.ClassDef):
                    for base in child.bases:
                        if (isinstance(base, ast.Attribute) and base.attr == 'AbstractHandler') or \
                           (isinstance(base, ast.Name) and base.id == 'AbstractHandler'):
                            handler_name = child.name
                            module_path = '.'.join(path.relative_to(root.parent).with_suffix('').parts)
                            # Record the module path and class name without importing
                            cls._handler_paths[handler_name] = module_path
                            break

    @classmethod
    def get_handler(cls, handler_type):
        if not cls._handlers:
            cls.discover_handlers()
        if handler_type not in cls._handlers:
            module_path = cls._handler_paths.get(handler_type)
            if module_path:
                # Dynamically import the module when requested
                module = importlib.import_module(module_path)
                handler_class = getattr(module, handler_type)
                if issubclass(handler_class, AbstractHandler):
                    cls._handlers[handler_type] = handler_class
                    return handler_class()
                else:
                    raise ValueError(f"The class {handler_type} is not a subclass of AbstractHandler")
            else:
                raise ValueError(f"Handler not found for type: {handler_type}")
        return cls._handlers[handler_type]()
