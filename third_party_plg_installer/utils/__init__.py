from mcdreforged.api.all import *


psi = ServerInterface.psi()
plgSelf = psi.get_self_metadata()
configDir = psi.get_data_folder()
MCDRConfig = psi.get_mcdr_config()
serverDir = MCDRConfig["working_directory"]