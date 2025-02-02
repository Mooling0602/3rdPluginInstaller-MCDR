from .utils import *
from .config import config_loader


def on_load(server: PluginServerInterface, prev_module):
    config_loader(server)