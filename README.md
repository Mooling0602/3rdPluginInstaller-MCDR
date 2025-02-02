# 3rdPluginInstaller-MCDR
适用于MCDReforged的第三方插件安装器，使用即代表您遵守相关协议。

## 使用协议及相关说明
1. 您在使用此工具安装任何插件前，需遵守对应插件的开源协议和其他相关的使用协议，遵守MCDReforged的开源协议和相关使用协议。
2. 您不得使用此工具下载任何侵权插件，下载任何插件前请自行确认其安全性和合法性，由于下载到不安全、非法的插件造成的任何后果，均由您自行承担。
3. 本插件使用GPLv3方式开源。
4. 此插件的开发和发布仅为了方便插件测试，若作为开发者，您不得通过调用此插件的方式来下载恶意插件依赖、后门程序，并且一般情况下，您应该首先将插件发布到官方的插件仓库以方便安装和管理，而不是调用此插件的接口。
5. 此插件允许用户使用自己的GitHub token获取信息，但用户需自行保证配置文件和命令输入内容的安全性，若无法保证，请勿使用！
> 如不使用token，可能会需要反复重试请求。
6. 此插件暂时只支持从GitHub仓库读取源码仓库信息并获取插件的已发布构建。
7. 若用户违反此协议，可能导致插件停止更新、删库跑路。
> 此插件将在开发完毕并确认符合官方插件仓库的投递规范后，投递到官方的插件仓库，但不保证能被通过。

## 用法
> 开发中内容，可能随时发生变动！

`!!plg install <url|filename|filepath>` - 从指定的plugin_info.json文件识别插件并下载最新的已发布构建，其中`filepath`为不在插件配置文件目录的其他路径下的plugin_info.json文件的完整路径

`!!plg install <url|filename|filepath> --latest` - 同上

`!!plg install <url|filename|filepath> <ver>` - 同上，但不是下载最新版，而是用户手动指定的版本，仅支持x.x.x的格式（vx.x.x不支持）

`!!plg subscribe <url|filename|filepath|list>` - 订阅自定义插件源，可方便日后更新插件，可指定多个源
> 不推荐通过保存多个plugin_info.json然后使用其进行更新，因为无法直接使用下面一条更加便捷的命令

`!!plg update <plugin_id|list>` - 更新插件，若插件不在官方插件仓库内，或者有自定义插件源，则直接从GitHub读取信息进行更新，可指定多个plugin_id

`!!plg update all` - 尝试更新所有第三方或有自定义更新源的插件

`!!plg update all --include-official` - 从官方插件仓库拉取plugin_info.json，添加自定义插件源并更新所有官方插件，然后更新所有第三方插件
> 风险有待评估，不会在插件的早期版本中做出来

`!!plg update <url|filename|filepath>` - 从指定的plugin_info.json文件识别插件并下载更新的已发布构建替换本地已安装的版本

`!!plg <args> --officailly` - 替代`!!MCDR plg <args>`使用，部分情况下不需要`--officially`参数

### 使用`--github-token <token>`参数
- **适用环境**

  从GitHub源安装、更新插件时

- 前提条件

  配置config.json中，`save_token`项为关闭状态

## 其他
开发中，咕咕咕……
