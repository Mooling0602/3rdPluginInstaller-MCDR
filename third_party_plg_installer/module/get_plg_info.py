import json
import os
import re
import third_party_plg_installer.plugin as plg
import third_party_plg_installer.config.applying as cfg

from urllib.parse import urlparse
from ..utils import configDir
from . import downloader


def classify_input(text: str) -> str|None:
    parsed = urlparse(text)
    if parsed.scheme and len(parsed.scheme) > 1 and parsed.netloc:
        return "url"
    if os.path.isabs(text) or ("/" in text or "\\" in text):
        return "filepath"
    filename_pattern = r'^[^<>:"/\\|?*]+\.[a-zA-Z0-9]+$'
    if re.match(filename_pattern, text):
        return "filename"
    return None

class getPluginInfo:
    def __call__(self, input: str):
        self.input = input
        self.type = classify_input(input)
        if self.type is not None:
            if self.type == "filepath":
                result = self.by_file_path(input)
            if self.type == "filename":
                result = self.by_file_name(input)
            if self.type == "url":
                result = self.by_file_url(input)
        else:
            result = None
        return result

    def by_file_path(self, filepath: str):
        encodings = cfg.plugin_config["encodings"]
        for i in encodings:
            try:
                with open(filepath, "r", encoding=i) as f:
                    return json.load(f)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {filepath} with encodings: {encodings}")
        
    def by_file_name(self, filename: str):
        encodings = cfg.plugin_config["encodings"]
        for i in encodings:
            try:
                with open(os.path.join(configDir, filename), "r", encoding=i) as f:
                    return json.load(f)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {os.path.join(configDir, filename)} with encodings: {encodings}")
    
    def by_file_url(self, url: str):
        target_path = os.path.join(configDir, "temp")
        if os.path.isfile(os.path.join(target_path, "plugin_info.json")):
            os.remove(os.path.join(target_path, "plugin_info.json"))
        if plg.stop_event.is_set():
            plg.stop_event.clear()
        with plg.download_lock:
            time_interval = cfg.plugin_config["download"]["interval"]
            cache_file = downloader(url, target_path, plg.stop_event, time_interval)
            if cache_file is None:
                raise FileExistsError("Can't download file that is not correct! You should download a json file which matches format of plugin info")
        encodings = cfg.plugin_config["encodings"]
        for i in encodings:
            if os.path.isfile(os.path.join(configDir, "temp", "plugin_info.json")):
                try:
                    with open(os.path.join(configDir, "temp", "plugin_info.json"), "r", encoding=i) as f:
                        return json.load(f)
                except UnicodeDecodeError:
                    continue
                raise UnicodeDecodeError(f"Failed to decode from url: {url} with encodings: {encodings}")
            else:
                raise FileNotFoundError(f"Failed to found correct file with filename \"plugin_info.json\"!")