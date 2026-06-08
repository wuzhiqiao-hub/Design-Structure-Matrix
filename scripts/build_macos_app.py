#!/usr/bin/env python3
"""Build a lightweight macOS .app bundle for the DSM/ISM UI."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "DSM-ISM"
APP_DIR = ROOT / "dist" / f"{APP_NAME}.app"
CONTENTS = APP_DIR / "Contents"
MACOS = CONTENTS / "MacOS"
RESOURCES = CONTENTS / "Resources"


INFO_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>zh_CN</string>
  <key>CFBundleDisplayName</key>
  <string>辽宁省大数据管理与优化决策重点实验室</string>
  <key>CFBundleExecutable</key>
  <string>DSM-ISM</string>
  <key>CFBundleIdentifier</key>
  <string>local.dsm-ism.app</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>DSM-ISM</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.13</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
"""


LAUNCHER = """#!/bin/sh
APP_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec /usr/bin/python3 "$APP_ROOT/Resources/DSM_ISM_App.py"
"""


def build() -> None:
    if APP_DIR.exists():
        shutil.rmtree(APP_DIR)

    MACOS.mkdir(parents=True)
    RESOURCES.mkdir(parents=True)

    (CONTENTS / "Info.plist").write_text(INFO_PLIST, encoding="utf-8")
    launcher_path = MACOS / APP_NAME
    launcher_path.write_text(LAUNCHER, encoding="utf-8")
    os.chmod(launcher_path, 0o755)

    for filename in ("index.html", "DSM_ISM_App.py"):
        shutil.copy2(ROOT / filename, RESOURCES / filename)

    print(f"Built {APP_DIR}")


if __name__ == "__main__":
    build()
