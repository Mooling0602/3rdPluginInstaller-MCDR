import json
import os

from ..utils import configDir


encodings = ['utf-8', 'gbk']

class getPluginInfoJSON:
    def by_file_path(filepath):
        for i in encodings:
            try:
                with open(filepath, "r", encoding=i) as f:
                    return json.load(f)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {filepath} with encodings: {encodings}")
        
    def by_file_name(filename: str):
        for i in encodings:
            try:
                with open(os.path.join(configDir, filename), "r", encoding=i) as f:
                    return json.load(f)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {os.path.join(configDir, filename)} with encodings: {encodings}")
    
    def by_file_url(url: str):
        pass
        for i in encodings:
            try:
                with open(os.path.join("cache", "plugin_info.json"), "r", encoding=i) as f:
                    return json.load(f)
            except UnicodeDecodeError:
                continue
            raise UnicodeDecodeError(f"Failed to decode from url: {url} with encodings: {encodings}")