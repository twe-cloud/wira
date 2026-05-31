# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Wira — Windows build."""

import sys
from pathlib import Path

import PyInstaller.building.build_main as build_main

agent_dir = Path(SPECPATH)

_find_binary_dependencies = build_main.find_binary_dependencies


def _find_binary_dependencies_without_neonize_import(binaries, import_packages, symlink_suppression_patterns):
    # neonize loads a native WhatsApp DLL at import time. On Windows runners,
    # importing it inside PyInstaller's isolated dependency scanner crashes the
    # scanner before it can build the app. The DLL is prepared by the workflow
    # and bundled as package data; runtime imports still load normally.
    import_packages = [package for package in import_packages if package != 'neonize']
    return _find_binary_dependencies(binaries, import_packages, symlink_suppression_patterns)


build_main.find_binary_dependencies = _find_binary_dependencies_without_neonize_import

a = Analysis(
    [str(agent_dir / 'gui.py')],
    pathex=[str(agent_dir)],
    binaries=[],
    datas=[
        (str(agent_dir / '.env.example'), '.'),
        (str(agent_dir / 'requirements.txt'), '.'),
    ],
    hiddenimports=[
        'neonize',
        'neonize.client',
        'neonize.events',
        'httpx',
        'openai',
        'anthropic',
        'ollama',
        'qrcode',
        'PIL',
        'config',
        'brain',
        'memory',
        'whatsapp',
        'drafts',
        'policy',
        'prompts',
        'auth',
        'onboarding',
        'review',
        'tkinter',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Wira',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=str(agent_dir / 'wira-icon.ico') if (agent_dir / 'wira-icon.ico').exists() else None,
)
