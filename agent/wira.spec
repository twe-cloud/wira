# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Wira.app — standalone Mac application."""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

agent_dir = Path(SPECPATH)

# neonize ships a native Go shared library (neonize-darwin-arm64.dylib) that it
# loads with ctypes.CDLL from its own package directory. It has no PyInstaller
# hook, so without collect_all the .app is missing the dylib entirely and all
# WhatsApp pairing/messaging fails at runtime. collect_all pulls the dylib, the
# generated proto modules, and package data into the bundle.
neonize_datas, neonize_binaries, neonize_hidden = collect_all('neonize')

a = Analysis(
    [str(agent_dir / 'gui.py')],
    pathex=[str(agent_dir)],
    binaries=[*neonize_binaries],
    datas=[
        (str(agent_dir / '.env.example'), '.'),
        (str(agent_dir / 'requirements.txt'), '.'),
        (str(agent_dir / 'wira-icon.icns'), '.'),
        *neonize_datas,
    ],
    hiddenimports=[
        *neonize_hidden,
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
        'local_models',
        'providers',
        'memory',
        'whatsapp',
        'drafts',
        'policy',
        'prompts',
        'paths',
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
    # Wira does not import torch/scipy; they were only ever swept in from a dirty
    # venv and bloated the bundle to ~435MB. Exclude them for a deterministic,
    # lean build (and a far faster notarization).
    excludes=['torch', 'torchvision', 'torchaudio', 'scipy'],
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
        'CFBundleShortVersionString': '1.0.7',
        'CFBundleVersion': '8',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'CFBundleDocumentTypes': [],
    },
)
