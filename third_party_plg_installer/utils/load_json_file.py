import json
import third_party_plg_installer.config.applying as cfg

def main(file_path: str) -> dict:
    encodings = cfg.plugin_config["encodings"]
    for i in encodings:
        try:
            with open(file_path, "r", encoding=i) as f:
                return json.load(f)
        except UnicodeEncodeError:
            continue
    raise UnicodeEncodeError

__all__ = ["main"]
import sys
sys.modules[__name__] = main