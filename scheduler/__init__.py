import importlib
try:
    importlib.import_module('library_management.admin')
except ImportError:
    pass