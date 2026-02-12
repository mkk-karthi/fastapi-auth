import os
import importlib

package_dir = os.path.dirname(__file__)

for module in os.listdir(package_dir):
    if module.endswith(".py") and module != "__init__.py":
        importlib.import_module(f"{__name__}.{module[:-3]}")
