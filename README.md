# 分流配置 v1

这是一套从零设计的 Clash Party（Mihomo）和 Quantumult X 配置模板。

规则源采用分工模式：blackmatrix7 负责跨客户端的服务规则，Loyalsoldier 负责 Clash Party 的基础规则，MetaCubeX 负责 Mihomo 地理数据。

## 当前分类

- ✈️X电报：Telegram、X
- 🤖 AI服务：OpenAI、ChatGPT、Codex、Claude、Gemini
- ▶️YouTube
- 🎵Spotify
- 🛒Amazon电商，默认直连
- 🇷🇺Wildberries电商，默认直连
- 🛡️ 广告拦截：`REJECT`，可切换为 `DIRECT` 关闭拦截
- 🛟 漏网之鱼：🚀 节点选择
- 节点：🇭🇰 香港、🇯🇵 日本、🇸🇬 新加坡、🇺🇸 美国、☁️ AWS亚马逊服务器节点
- 国内域名和中国大陆 IP：通过 GeoSite/GeoIP 规则默认直连，不单独创建策略组。

## 规则源

- 服务规则：[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
- Clash Party 基础规则：[Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)，通过 GitHub Actions 定期构建
- Mihomo 地理数据：[MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat)
- Amazon 电商、Wildberries：本仓库自定义规则

## 使用前需要修改

主仓库地址：<https://github.com/MrGuAm/personal-proxy-rules>

配置和自定义规则已经使用该仓库的 Raw 地址。

## 重要说明

- `mihomo.yaml` 中的节点由 SubStore 合并你的机场订阅后提供。
- `quantumult-x.conf` 中的节点标签由 SubStore/圈X订阅提供；本文件负责策略组和远程分流。
- AWS亚马逊服务器节点是根据订阅节点名称筛选出来的节点组，名称中需要包含 `AWS`、`亚马逊` 或 `Amazon`。
- Amazon电商规则只负责 Amazon 购物网站，默认直连。
- 地区测速依赖订阅节点名称包含地区关键词，例如“香港 / HK / Hong Kong”。如果机场使用完全不同的命名，需要调整正则表达式。
- blackmatrix7 和 Loyalsoldier 的远程规则更新周期设为 24 小时；规则源本身的实际发布时间由上游维护计划决定。
- Mihomo 的 `geosite.dat` 和 `geoip-lite.dat` 使用 MetaCubeX 最新发布地址。
