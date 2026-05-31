# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Wira.app — standalone Mac application."""

import sys
from pathlib import Path

agent_dir = Path(SPECPATH)

a = Analysis(
    [str(agent_dir / 'gui.py')],
    pathex=[str(agent_dir)],
    binaries=[],
    datas=[
        (str(agent_dir / '.env.example'), '.'),
        (str(agent_dir / 'requirements.txt'), '.'),
        (str(agent_dir / 'wira-icon.icns'), '.'),
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
        'magic',
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
    [],
    exclude_binaries=True,
    name='Wira',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Wira',
)

app = BUNDLE(
    coll,
    name='Wira.app',
    icon=str(agent_dir / 'wira-icon.icns'),
    bundle_identifier='biz.nibiashara.wira',
    info_plist={
        'CFBundleName': 'Wira',
        'CFBundleDisplayName': 'Wira',
        'CFBundleShortVersionString': '1.0.3',
        'CFBundleVersion': '4',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'CFBundleDocumentTypes': [],
    },
)
