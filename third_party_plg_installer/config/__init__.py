import third_party_plg_installer.config.applying as cfg

from .default import *
from ..utils import tr
from mcdreforged.api.types import PluginServerInterface


def config_loader(server: PluginServerInterface):
    cfg.plugin_config = server.load_config_simple('config.json', default_config)
    server.logger.info(tr("on_load"))