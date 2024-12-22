# collectors/__init__.py

import os
import importlib
from typing import List
from collectors.base_collector import Collector
import logging

def load_collectors(config: dict) -> List[Collector]:
    """
    Dynamically load all collector classes from the collectors directory.
    Args:
        config: Configuration dictionary.
    Returns:
        A list of instantiated collector objects.
    """
    collectors = []
    collectors_dir = os.path.dirname(__file__)
    for filename in os.listdir(collectors_dir):
        if filename.endswith(".py") and filename != "base_collector.py" and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"collectors.{module_name}")
                # Iterate through attributes to find Collector subclasses
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if isinstance(cls, type) and issubclass(cls, Collector) and cls is not Collector:
                        collector_instance = cls(config)
                        collectors.append(collector_instance)
                        logging.info(f"Loaded collector: {cls.__name__}")
            except Exception as e:
                logging.error(f"Failed to load collector '{module_name}': {e}")
    return collectors
