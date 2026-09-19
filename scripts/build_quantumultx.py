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
PERSONAL_OVERRIDE_SECTIONS = {"policy", "filter_remote", "filter_local"}


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


def build(personal_path: Path, output_path: Path) -> None:
    upstream_prefix, upstream_sections = split_sections(fetch_upstream())
    _, personal_sections = split_sections(personal_path.read_text(encoding="utf-8"))
    personal_map = {name: body for name, body in personal_sections}

    output = [upstream_prefix]
    for name, body in upstream_sections:
        if name == "server_remote":
            # The upstream file contains a temporary public node subscription.
            # Nodes are supplied separately by the user's Sub-Store workflow.
            continue
        if name in PERSONAL_OVERRIDE_SECTIONS and name in personal_map and meaningful(personal_map[name]):
            output.append(personal_map[name].rstrip() + "\n")
        else:
            output.append(body)

    output_path.write_text("\n".join(part.rstrip("\n") for part in output).rstrip() + "\n", encoding="utf-8")


def validate(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    _, sections = split_sections(text)
    names = [name for name, _ in sections]
    if names.count("policy") != 1 or names.count("filter_remote") != 1 or names.count("filter_local") != 1:
        raise ValueError("generated config must have exactly one policy/filter_remote/filter_local section")
    if "server_remote" in names:
        raise ValueError("generated config must not include upstream temporary server_remote")
    if "[rewrite_remote]" not in text or "BiliBiliAdsLite.conf" not in text:
        raise ValueError("official rewrite_remote section was not included")
    if "quantumult-x.conf" not in text and "🤖 AI服务" not in text:
        raise ValueError("personal policy overlay was not included")
    if "p12 =" in text or "passphrase =" in text:
        raise ValueError("private MITM material must not be published by this repository")
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
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_quantumultx.py personal.conf output.conf")
    output = Path(sys.argv[2])
    build(Path(sys.argv[1]), output)
    validate(output)


if __name__ == "__main__":
    main()
