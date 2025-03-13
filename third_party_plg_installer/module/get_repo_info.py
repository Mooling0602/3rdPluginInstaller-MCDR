import json
import re
import requests
import third_party_plg_installer.config.applying as cfg

from datetime import datetime


def get_plugin_repo(plugin_info_path):
    with open(plugin_info_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_next_link(link_header):
    if not link_header:
        return None
    links = link_header.split(',')
    next_url = None
    for link in links:
        parts = link.split(';')
        if len(parts) < 2:
            continue
        url_part = parts[0].strip()
        rel_part = parts[1].strip()
        if rel_part == 'rel="next"':
            # Remove < and >
            next_url = url_part[1:-1]
            break
    return next_url

def fetch_releases(repository_url, headers, timeout=5):
    parts = repository_url.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid repo address!")
    owner, repo = parts[-2], parts[-1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    releases = []
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    while url:
        print(f"Getting: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
        except requests.exceptions.Timeout:
            print("Request timed out, please check network connections.")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            break

        if resp.status_code != 200:
            raise Exception(f"Failed to fetch release: HTTP {resp.status_code}, response message:{resp.text}")
        data = resp.json()
        releases.extend(data)
        url = get_next_link(resp.headers.get("Link", None))
    return releases

def get_all_releases(plugin_info_path, github_token=None):
    metadata = get_plugin_repo(plugin_info_path)
    plugin_id = metadata.get("id")
    repository_url = metadata.get("repository")
    
    if not plugin_id or not repository_url:
        raise ValueError("plugin_info.json missing necessary keys: id or repository")
    
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    timeout = cfg.plugin_config["timeout"]
    all_releases = fetch_releases(repository_url, headers, timeout=timeout)
    return all_releases, plugin_id

def is_valid_release(release, plugin_id):
    if release.get("prerelease", False):
        return False

    tag = release.get("tag_name", "")

    pattern_version = r"^(v)?\d+\.\d+\.\d+$"  # e.g. 1.2.3 or v1.2.3
    pattern_with_id = rf"^{re.escape(plugin_id)}-(v)?\d+\.\d+\.\d+$"  # like my_plugin-1.2.3 or my_plugin-v1.2.3

    if not (re.match(pattern_version, tag) or re.match(pattern_with_id, tag)):
        return False

    assets = release.get("assets", [])
    valid_asset = any(asset.get("name", "").lower().endswith((".mcdr", ".pyz")) for asset in assets)
    return valid_asset

def parse_iso_datetime(dt_str):
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None

def get_valid_plugin_versions(plugin_info_path, timeout=5, github_token=None):
    all_releases, plugin_id = get_all_releases(plugin_info_path, github_token)
    version_list = []
    for release in all_releases:
        ver_info = {
            "version": release.get("tag_name"),
            "published_at": release.get("published_at"),
            "download_url": None,
            "is_pre_release": bool(release.get("prerelease", False))
        }
        if not ver_info["is_pre_release"] and is_valid_release(release, plugin_id):
            asset = next((a for a in release.get("assets", []) if a.get("name", "").lower().endswith((".mcdr", ".pyz"))), None)
            ver_info["download_url"] = asset.get("browser_download_url") if asset else None
        version_list.append(ver_info)
    
    version_list.sort(key=lambda v: parse_iso_datetime(v["published_at"]) or datetime.min)
    
    stable_versions = [v for v in version_list if not v["is_pre_release"]]
    latest_stable = None
    if stable_versions:
        latest_stable = max(stable_versions, key=lambda x: parse_iso_datetime(x["published_at"]) or datetime.min)
    for v in version_list:
        v["is_latest"] = (latest_stable is not None and v["version"] == latest_stable["version"])
    return version_list