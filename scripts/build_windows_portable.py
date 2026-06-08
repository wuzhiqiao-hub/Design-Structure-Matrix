#!/usr/bin/env python3
"""Build a Windows portable bundle for the DSM/ISM browser app."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "dist" / "windows"
APP_DIR = OUT_ROOT / "DSM-ISM-Windows"
ZIP_PATH = OUT_ROOT / "DSM-ISM-Windows.zip"


CMD_LAUNCHER = r"""@echo off
set "APP_DIR=%~dp0"
start "" "%APP_DIR%index.html"
"""


VBS_LAUNCHER = r'''Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.Run """" & appDir & "\index.html" & """", 1, False
'''


README = """辽宁省大数据管理与优化决策重点实验室 - Windows 便携版
====================================

运行方式
--------

1. 解压 DSM-ISM-Windows.zip
2. 打开 DSM-ISM-Windows 文件夹
3. 双击 DSM-ISM.vbs 或 DSM-ISM.cmd

说明
----

- 这个版本不需要安装 Python、Node.js 或 npm。
- 程序会使用 Windows 默认浏览器打开 index.html。
- 所有计算都在本机浏览器中完成，不会上传数据。
- 如果系统拦截 .vbs 文件，可以双击 DSM-ISM.cmd，或直接双击 index.html。

主要功能
--------

- 设置任务数量，自动生成 N x N 关系矩阵
- 编辑每个任务名称
- 填写 0 到 1 的连续关系强度
- 调整阈值并查看 ISM 层级
- 查看关系图、可达矩阵和完整中间过程矩阵
- 导出 CSV 和分析报告
"""


def build() -> None:
    if APP_DIR.exists():
        shutil.rmtree(APP_DIR)
    APP_DIR.mkdir(parents=True)

    shutil.copy2(ROOT / "index.html", APP_DIR / "index.html")
    (APP_DIR / "DSM-ISM.cmd").write_text(CMD_LAUNCHER, encoding="utf-8")
    (APP_DIR / "DSM-ISM.vbs").write_text(VBS_LAUNCHER, encoding="utf-8")
    (APP_DIR / "README-Windows.txt").write_text(README, encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(APP_DIR.rglob("*")):
            archive.write(path, path.relative_to(OUT_ROOT))

    print(f"Built {APP_DIR}")
    print(f"Built {ZIP_PATH}")


if __name__ == "__main__":
    build()
