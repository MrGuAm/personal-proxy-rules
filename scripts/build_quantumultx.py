#!/usr/bin/env python3
"""Build a Quantumult X config from Cuttlefish upstream plus personal sections."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


UPSTREAM_URL = "https://ddgksf2013.top/Profile/QuantumultX.conf"
SECTION_RE = re.compile(r"^\[([^\]]+)\]\s*$")
SECTION_NAMES = {"general", "task_local", "rewrite_local", "rewrite_remote", "server_local", "server_remote", "dns", "policy", "filter_remote", "filter_local", "http_backend", "mitm"}
PERSONAL_OVERRIDE_SECTIONS = {"policy"}
OFFICIAL_SERVER_REMOTE = """[server_remote]

# > 墨鱼官方临时订阅
https://raw.githubusercontent.com/Ruk1ng001/freeSub/main/clash.yaml#delreg=.*&rename=@tg%40ddgksf2021-+@num-$index7, tag=🐟临时使用, update-interval=3600, opt-parser=true, enabled=true
"""

# 官方分流使用官方策略组名称。合并到个人策略组时必须改成实际存在的名称。
POLICY_MAP = {
    "声田音乐": "🎵Spotify",
    "国际媒体": "🚀 节点选择",
    "哔哩哔哩": "direct",
    "苹果服务": "direct",
    "全球加速": "🚀 节点选择",
    "兜底分流": "🛟 漏网之鱼",
}


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    matches = list(re.finditer(r"(?m)^\[([^\]]+)\]\s*$", text))
    if not matches:
        raise ValueError("configuration has no Quantumult X sections")
    prefix = text[: matches[0].start()]
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[match.start():end]))
    return prefix, sections


def meaningful(section: str) -> bool:
    return any(line.strip() and not line.lstrip().startswith(("#", ";")) for line in section.splitlines()[1:])


def body_lines(section: str) -> list[str]:
    """Return active (non-comment) lines below a section header."""
    return [
        line.strip()
        for line in section.splitlines()[1:]
        if line.strip() and not line.lstrip().startswith(("#", ";"))
    ]


def resource_url(line: str) -> str:
    return line.split(",", 1)[0].strip()


def map_official_policy(line: str) -> str:
    """Map an official filter resource to one of the personal policy groups."""
    match = re.search(r"force-policy=([^,]+)", line)
    if not match:
        return line
    policy = match.group(1).strip()
    if "ddgksf2013.top/filter/Ai.yaml" in line:
        replacement = "🤖 AI平台"
    elif policy == "美国节点":
        replacement = "🇺🇸 美国节点"
    elif policy == "reject":
        replacement = "🛡️ 广告拦截"
    else:
        replacement = POLICY_MAP.get(policy, policy)
    return line[:match.start(1)] + replacement + line[match.end(1):]


def merge_filter_remote(official: str, personal: str) -> str:
    """Merge resource lists, preferring personal entries with the same URL."""
    personal_lines = body_lines(personal)
    personal_urls = {resource_url(line) for line in personal_lines}
    official_lines = [
        map_official_policy(line)
        for line in body_lines(official)
        if resource_url(line) not in personal_urls
    ]

    # Put broad catch-all resources last so they cannot shadow personal service rules.
    broad_markers = ("/Streaming.list", "/Proxy.list", "/ASN.China.list")
    specific = [line for line in official_lines if not any(marker in line for marker in broad_markers)]
    broad = [line for line in official_lines if any(marker in line for marker in broad_markers)]

    lines = ["[filter_remote]", "", "# ======= 墨鱼官方规则（策略已映射到个人策略组） ======= #"]
    lines.extend(specific)
    lines.extend(["", "# ======= 个人规则（同 URL 时优先） ======= #"])
    lines.extend(personal_lines)
    lines.extend(["", "# ======= 墨鱼官方宽泛/兜底规则（放在最后） ======= #"])
    lines.extend(broad)
    return "\n".join(lines).rstrip() + "\n"


def local_rule_key(line: str) -> tuple[str, ...]:
    fields = tuple(field.strip().lower() for field in line.split(","))
    if not fields:
        return fields
    if fields[0] == "final":
        return ("final",)
    return fields[:2]


def merge_filter_local(official: str, personal: str) -> str:
    """Merge local rules by match target, preferring personal policy choices."""
    personal_lines = body_lines(personal)
    personal_keys = {local_rule_key(line) for line in personal_lines}
    official_lines = [line for line in body_lines(official) if local_rule_key(line) not in personal_keys]
    lines = ["[filter_local]", "", "# ======= 墨鱼官方本地规则 ======= #"]
    lines.extend(official_lines)
    lines.extend(["", "# ======= 个人本地规则（重复目标时优先） ======= #"])
    lines.extend(personal_lines)
    return "\n".join(lines).rstrip() + "\n"


def enable_ipv6(dns_section: str) -> str:
    """Follow the official DNS section but remove its IPv6 disabling directive."""
    lines = []
    for line in dns_section.splitlines():
        if line.strip().lower() == "no-ipv6":
            continue
        if "QuantumultX开启IPV6方法" in line:
            lines.append("# > 已按个人要求删除 no-ipv6；还需在 Quantumult X 的 VPN 设置中开启兼容性增强")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def fetch_upstream() -> str:
    override = os.environ.get("OFFICIAL_CONFIG_FILE")
    if override:
        return Path(override).read_text(encoding="utf-8")
    result = subprocess.run(
        [
            "curl", "--fail", "--location", "--silent", "--show-error",
            "--retry", "5", "--retry-all-errors", "--retry-delay", "3",
            "--connect-timeout", "20", "--max-time", "120",
            "-A", "QuantumultX-PersonalConfig/1.0", UPSTREAM_URL,
        ],
        check=True,
        capture_output=True,
    )
    return result.stdout.decode("utf-8")


def build(personal_path: Path, output_path: Path, private_path: Path | None = None) -> None:
    upstream_prefix, upstream_sections = split_sections(fetch_upstream())
    _, personal_sections = split_sections(personal_path.read_text(encoding="utf-8"))
    personal_map = {name: body for name, body in personal_sections}
    private_map = {}
    if private_path:
        _, private_sections = split_sections(private_path.read_text(encoding="utf-8"))
        private_map = {name: body for name, body in private_sections}

    output = [upstream_prefix]
    for name, body in upstream_sections:
        if name == "server_remote":
            output.append(private_map.get(name, OFFICIAL_SERVER_REMOTE))
            continue
        if name == "dns":
            output.append(enable_ipv6(body))
            continue
        if name == "filter_remote":
            output.append(merge_filter_remote(body, personal_map[name]))
            continue
        if name == "filter_local":
            output.append(merge_filter_local(body, personal_map[name]))
            continue
        if name == "mitm" and name in private_map and meaningful(private_map[name]):
            output.append(private_map[name].rstrip() + "\n")
            continue
        if name in PERSONAL_OVERRIDE_SECTIONS and name in personal_map and meaningful(personal_map[name]):
            output.append(personal_map[name].rstrip() + "\n")
        else:
            output.append(body)

    output_path.write_text("\n".join(part.rstrip("\n") for part in output).rstrip() + "\n", encoding="utf-8")


def validate(path: Path, private_overlay: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    _, sections = split_sections(text)
    names = [name for name, _ in sections]
    if names.count("policy") != 1 or names.count("filter_remote") != 1 or names.count("filter_local") != 1:
        raise ValueError("generated config must have exactly one policy/filter_remote/filter_local section")
    if names.count("server_remote") != 1:
        raise ValueError("generated config must have exactly one server_remote section")
    if private_overlay:
        if "p12 =" not in text or "passphrase =" not in text:
            raise ValueError("private MITM material was not included")
    else:
        if "Ruk1ng001/freeSub" not in text:
            raise ValueError("official server_remote subscription was not included")
        if "gist.githubusercontent.com" in text:
            raise ValueError("personal subscription URL must not be published")
        if "p12 =" in text or "passphrase =" in text:
            raise ValueError("private MITM material must not be published")
    if re.search(r"(?m)^\s*no-ipv6\s*$", text):
        raise ValueError("generated config must leave IPv6 enabled")
    if "[rewrite_remote]" not in text or "BiliBiliAdsLite.conf" not in text:
        raise ValueError("official rewrite_remote section was not included")
    if "quantumult-x.conf" not in text and "🤖 AI平台" not in text:
        raise ValueError("personal policy overlay was not included")
    if re.search(r"(?i)^(?:vmess|vless|trojan|ss|ssr|hysteria2?)://", text, re.MULTILINE):
        raise ValueError("node URLs must not be committed")

    policies = set()
    for line in text.splitlines():
        match = re.match(r"^static=([^,]+)", line)
        if match:
            policies.add(match.group(1).strip())
        match = re.match(r"^url-latency-benchmark=([^,]+)", line)
        if match:
            policies.add(match.group(1).strip())
        match = re.match(r"^available=([^,]+)", line)
        if match:
            policies.add(match.group(1).strip())
    policies.update({"direct", "reject", "proxy"})

    missing = set()
    for line in text.splitlines():
        match = re.search(r"force-policy=([^,]+)", line)
        if match and match.group(1).strip() not in policies:
            missing.add(match.group(1).strip())
        match = re.match(r"^(?:host|host-suffix|host-keyword|ip-cidr|ip6-cidr|geoip|final),\s*(.+)$", line)
        if match:
            fields = [field.strip() for field in line.split(",")]
            target = fields[1] if fields[0] == "final" else fields[2]
            if target not in policies:
                missing.add(target)
    if missing:
        raise ValueError("rules reference missing policies: " + ", ".join(sorted(missing)))


def main() -> None:
    if len(sys.argv) not in {3, 4}:
        raise SystemExit("usage: build_quantumultx.py personal.conf output.conf [private-overlay.conf]")
    output = Path(sys.argv[2])
    private_path = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    build(Path(sys.argv[1]), output, private_path)
    validate(output, private_path is not None)


if __name__ == "__main__":
    main()
