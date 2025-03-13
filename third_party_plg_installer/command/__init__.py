import json
import os
import subprocess
import sys
import third_party_plg_installer.plugin as plg
import third_party_plg_installer.config.applying as cfg

from mcdreforged.api.all import *
from ..utils import configDir, psi
from ..module.get_plg_info import getPluginInfo, classify_input
from ..module.get_repo_info import get_valid_plugin_versions
from ..module import downloader


get_plg_info = getPluginInfo()
builder = SimpleCommandBuilder()

def command_register(server: PluginServerInterface):
    builder.arg('filename|filepath|url', Text)
    builder.arg('url', Text)
    builder.arg('plugin_id', Text)
    builder.arg('github_token', Text)
    builder.arg('package_name', Text)
    builder.arg('file_path', Text)
    builder.register(server)

@builder.command('!!plg source add <filename|filepath|url>')
@new_thread('AddPluginSource')
def on_add_source(src: CommandSource, ctx: CommandContext):
    if plg.download_lock.locked():
        src.reply("下载线程正在被占用，请手动暂停或等待其完成！")
    else:
        input = ctx["filename|filepath|url"]
        plugin_info = get_plg_info(input)
        plugin_id =  plugin_info["id"]
        plugin_repo = plugin_info["repository"]
        single_plugin_info = {}
        single_plugin_info["id"] = plugin_id
        single_plugin_info["repository"] = plugin_repo
        local_repo_path = os.path.join(configDir, "local_repo", plugin_id)
        os.makedirs(local_repo_path, exist_ok=True)
        if os.path.isfile(local_repo_path):
            os.remove(os.path.join(local_repo_path, "plugin_info.json"))
        with open(os.path.join(local_repo_path, "plugin_info.json"), "w", encoding="utf-8") as f:
            json.dump(single_plugin_info, f, ensure_ascii=False, indent=4)
            src.reply("插件源已添加或更新！")

@builder.command('!!download stop')
def on_stop_download(src: CommandSource):
    plg.stop_event.set()
    src.reply("已尝试暂停所有下载线程！")

@builder.command('!!download <url>')
@new_thread('DownloadFile')
def on_download(src: CommandSource, ctx: CommandContext):
    if plg.download_lock.locked():
        src.reply("下载线程正在被占用，请手动暂停或等待其完成！")
    else:
        url = ctx["url"]
        if classify_input(url) == "url":
            if plg.stop_event.is_set():
                plg.stop_event.clear()
            with plg.download_lock:
                target_path = "cache"
                os.makedirs(target_path, exist_ok=True)
                downloader(url, target_path, plg.stop_event, 5, False)
        else:
            src.reply("你输入的并非有效链接！")

def query_task(src: CommandSource, ctx: CommandContext, github_token: str=None):
    working_path = os.path.join(configDir, "local_repo", ctx["plugin_id"])
    if not os.path.exists(working_path):
        src.reply("请先添加插件源！使用!!plg source add <filename|filepath|url>")
    else:
        if src.has_permission(4):
            plg_version_info = get_valid_plugin_versions(os.path.join(working_path, "plugin_info.json"), 5, github_token)
            ver_list_max = cfg.plugin_config["ver_list_max"]
            if len(plg_version_info) > ver_list_max:
                src.reply(f"有效的插件版本数量过多（大于{ver_list_max}个），将只显示最新版本的内容。")
                for i in plg_version_info:
                    if i["is_latest"] is True:
                        if i["download_url"] is not None:
                            src.reply(f"插件最新版本：{i["version"]}")
                            src.reply(f"下载链接：{i["download_url"]}")
            else:
                for i in plg_version_info:
                    if i["is_latest"] is True:
                        if i["download_url"] is not None:
                            src.reply(f"最新版本：{i["version"]}")
                            src.reply(f"下载链接：{i["download_url"]}\n \n")
                    else:
                        if i["download_url"] is not None:
                            src.reply(f"版本号：{i["version"]}")
                            src.reply(f"下载链接：{i["download_url"]}\n \n")

@builder.command('!!plg query <plugin_id>')
def on_query(src: CommandSource, ctx: CommandContext):
    query_task(src, ctx)

@builder.command('!!plg query <plugin_id> --github-token <github_token>')
def on_query_with_github_token(src: CommandSource, ctx: CommandContext):
    query_task(src, ctx, github_token=ctx["github_token"])

@builder.command('!!pip install <package_name>')
@new_thread('InstallPyPI')
def on_pip_install(src: CommandSource, ctx: CommandContext):
    if src.is_console:
        psi.logger.info(f"正在安装你指定的PyPI依赖：{ctx["package_name"]}")
        try:
            resp = subprocess.check_call(['pip', 'install', ctx["package_name"]])
            if resp == 0:
                psi.logger.info("操作执行完成！")
            else:
                psi.logger.info(f"可能发生异常，返回代码为：{resp}")
        except subprocess.CalledProcessError:
            psi.logger.error(f"似乎包名不对或者其他原因，你指定的PyPI包安装时发生错误，大概率安装失败！")
    else:
        src.reply("请在控制台执行，以查看安装时输出的详细日志！")

@builder.command('!!pip install -r <file_path>')
@new_thread('InstallPyPI')
def on_pip_install(src: CommandSource, ctx: CommandContext):
    if src.is_console:
        psi.logger.info(f"正在从指定的文件：{ctx["file_path"]}中安装里面指定的PyPI依赖")
        try:
            resp = subprocess.check_call(['pip', 'install', '-r', ctx["file_path"]])
            if resp == 0:
                psi.logger.info("操作执行完成！")
            else:
                psi.logger.info(f"可能发生异常，返回代码为：{resp}")
        except subprocess.CalledProcessError:
            psi.logger.error(f"似乎包名不对或者其他原因，你指定的PyPI包安装时发生错误，大概率安装失败！")
    else:
        src.reply("请在控制台执行，以查看安装时输出的详细日志！")

