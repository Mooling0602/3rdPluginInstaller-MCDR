import requests
import os
import time

from ..utils import configDir, psi
from urllib.parse import urlparse


def main(url: str, target_path: str, stop_event, progress_interval: int, file_verify: bool=True):
    # 解析 URL 获取文件名
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    
    if file_verify:
        if not file_name.endswith(".json"):
            return None
    
        if file_name != "plugin_info.json":
            file_name = "plugin_info.json"
    
    temp_save_path = os.path.join(target_path, f"{file_name}.part")
    final_save_path = os.path.join(target_path, file_name)

    # 初始化下载状态
    downloaded_size = 0
    if os.path.exists(temp_save_path):
        # 如果文件已存在，获取已下载的大小（用于断点续传）
        downloaded_size = os.path.getsize(temp_save_path)
        psi.logger.info(f"检测到未完成的下载。已下载 {downloaded_size} 字节，将继续下载。")
        psi.logger.info(f"进度提示间隔为：{progress_interval} 秒")
    else:
        psi.logger.info(f"开始下载 {file_name} 到 {final_save_path}")

    # 发送 HEAD 请求以获取文件总大小
    response = requests.head(url)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))

    if total_size > 0:
        psi.logger.info(f"已下载：{downloaded_size}/{total_size} 字节 ({(downloaded_size / total_size) * 100:.2f}%)")
    else:
        psi.logger.info("无法获取文件的总大小，将不能显示进度！")

    # 设置请求头，支持断点续传（需服务器支持 Range 请求）
    headers = {"Range": f"bytes={downloaded_size}-"} if downloaded_size > 0 else {}

    # 发送 GET 请求（stream=True 启用流式下载）
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    # 确保保存目录存在
    os.makedirs(os.path.join(configDir, "temp"), exist_ok=True)

    # 记录上次进度提示的时间
    last_progress_time = time.time()

    # 以追加模式打开文件
    with open(temp_save_path, "ab") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # 过滤空块（保持活跃连接）
                f.write(chunk)
                downloaded_size += len(chunk)

                # 检查是否到达下一个时间间隔
                current_time = time.time()
                if current_time - last_progress_time >= progress_interval:
                    if total_size > 0:
                        psi.logger.info(f"已下载：{downloaded_size}/{total_size} 字节 ({(downloaded_size / total_size) * 100:.2f}%)")
                    else:
                        psi.logger.info(f"已下载：{downloaded_size} 字节")
                    last_progress_time = current_time # 更新上次提示时间

                # 检查是否设置了停止事件
                if stop_event.is_set():
                    psi.logger.info("下载被用户中断。")
                    return downloaded_size

    # 下载完成后重命名文件
    os.rename(temp_save_path, final_save_path)
    psi.logger.info(f"下载完成。文件已保存为：{final_save_path}")
    return downloaded_size

__all__ = ["main"]
import sys
sys.modules[__name__] = main