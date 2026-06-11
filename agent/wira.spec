# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Wira.app — standalone Mac application."""

import ctypes.util
import os
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


def _find_libmagic():
    """Locate the native libmagic on the build host.

    neonize does an unconditional top-level ``import magic`` (python-magic),
    which loads libmagic at import time. macOS ships no system libmagic and a
    buyer has no Homebrew/MacPorts, so unless we bundle it the app crashes the
    moment the user reaches WhatsApp pairing. Fail the build loudly if it is
    missing here rather than shipping another broken DMG.
    """
    found = ctypes.util.find_library('magic')
    if found and os.path.exists(found):
        return found
    for candidate in (
        '/opt/homebrew/lib/libmagic.dylib',
        '/usr/local/lib/libmagic.dylib',
        '/opt/local/lib/libmagic.dylib',
    ):
        if os.path.exists(candidate):
            return candidate
    raise SystemExit(
        'wira.spec: libmagic not found on the build host. '
        'Run `brew install libmagic` before building.'
    )


def _find_magic_db():
    for candidate in (
        '/opt/homebrew/share/misc/magic.mgc',
        '/usr/local/share/misc/magic.mgc',
        '/opt/local/share/misc/magic.mgc',
    ):
        if os.path.exists(candidate):
            return candidate
    return None


_libmagic = _find_libmagic()
_magic_db = _find_magic_db()
# Ship libmagic.dylib next to the bundled binaries and its compiled DB as data;
# rthook_libmagic.py points python-magic at both at runtime.
magic_binaries = [(_libmagic, '.')]
magic_datas = [(_magic_db, '.')] if _magic_db else []

a = Analysis(
    [str(agent_dir / 'gui.py')],
    pathex=[str(agent_dir)],
    binaries=[*neonize_binaries, *magic_binaries],
    datas=[
        (str(agent_dir / '.env.example'), '.'),
        (str(agent_dir / 'requirements.txt'), '.'),
        (str(agent_dir / 'wira-icon.icns'), '.'),
        *neonize_datas,
        *magic_datas,
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
    runtime_hooks=[str(agent_dir / 'rthook_libmagic.py')],
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
