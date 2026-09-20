# 分流配置 v1

## Quantumult X 自动配置

`quantum-x-auto.conf` 由 GitHub Actions 自动生成：以墨鱼官方配置为上游，采用官方通用设置、任务和重写；采用个人策略组；合并官方与个人分流并自动去重。

Quantumult X 订阅地址：

`https://raw.githubusercontent.com/MrGuAm/personal-proxy-rules/main/quantum-x-auto.conf`

官方配置每 6 小时检查一次。生成时会保留官方 DNS，但删除 `no-ipv6` 以允许 IPv6，并采用墨鱼官方的临时节点订阅。个人节点订阅地址不会写入本仓库。

### 本地私密合成

个人节点订阅和 MITM 证书不能与公开 GitHub 配置共存。将 `quantumult-x.private.conf.example` 复制为 `quantumult-x.private.conf` 并填写私密内容后，在本机运行：

```bash
bash scripts/build_quantumultx_local.sh
```

这会生成被 Git 忽略的 `quantum-x-local.conf`，其中才包含个人节点订阅和 MITM。圈 X 使用该本地文件时，配置更新需要在本机重新合成；公开 Raw 自动配置不含任何私密数据。

合并分流时，相同远程规则 URL 和相同本地匹配目标以个人配置为准。官方规则引用的策略会映射到现有个人策略组，宽泛的国际媒体、全球代理和国内规则放在个人服务规则之后，避免提前覆盖 Telegram、AI、YouTube、电商等个人分流。

这是一套从零设计的 Clash Party（Mihomo）和 Quantumult X 配置模板。

规则源采用分工模式：blackmatrix7 负责跨客户端的服务规则，Loyalsoldier 负责 Clash Party 的基础规则，MetaCubeX 负责 Mihomo 地理数据。

## 当前分类

- ✈️X电报：Telegram、X
- 🤖 AI平台：OpenAI、ChatGPT、Codex、Claude、Gemini
- ▶️YouTube
- 🎵Spotify
- Apple 服务：直连
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
- AWS 服务、Amazon 电商、Wildberries：本仓库自定义规则

## 使用前需要修改

主仓库地址：<https://github.com/MrGuAm/personal-proxy-rules>

配置和自定义规则已经使用该仓库的 Raw 地址。

## 重要说明

- `mihomo.yaml` 中的节点由 SubStore 合并你的机场订阅后提供。
- `quantumult-x.conf` 中的节点标签由 SubStore/圈X订阅提供；本文件负责策略组和远程分流。
- AWS亚马逊服务器节点是根据订阅节点名称筛选出来的节点组，名称中需要包含 `AWS`、`亚马逊` 或 `Amazon`。
- AWS 控制台和云服务域名默认直连，不会被 Amazon 电商规则覆盖。
- Apple 服务（包括 `*.apple.com`、`*.icloud.com` 等）默认直连。
- Amazon电商规则只负责 Amazon 购物网站，默认直连。
- 地区测速依赖订阅节点名称包含地区关键词，例如“香港 / HK / Hong Kong”。如果机场使用完全不同的命名，需要调整正则表达式。
- blackmatrix7 和 Loyalsoldier 的远程规则更新周期设为 24 小时；规则源本身的实际发布时间由上游维护计划决定。
- Mihomo 的 `geosite.dat` 和 `geoip-lite.dat` 使用 MetaCubeX 最新发布地址。
