from .utils import *
from .config import config_loader
from .command import command_register


def on_load(server: PluginServerInterface, prev_module):
    config_loader(server)
    command_register(server)