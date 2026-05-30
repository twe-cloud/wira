# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Wira — Windows build."""

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
