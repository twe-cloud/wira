"""PyInstaller runtime hook: make python-magic find the bundled libmagic.

neonize does an unconditional top-level ``import magic`` (python-magic), and
python-magic loads the native libmagic at import time. Its loader only probes
Homebrew/MacPorts paths (/opt/homebrew, /usr/local, /opt/local, Cellar) that a
non-developer buyer's Mac does not have, so the import raises ImportError and
crashes the whole app the moment the user reaches WhatsApp pairing.

We bundle libmagic.dylib + magic.mgc into the app (see wira.spec). This hook
runs before any application code — therefore before ``import magic`` — and
points python-magic's loader at the bundled copies by patching
``ctypes.util.find_library`` (the loader's first candidate) and setting MAGIC
(libmagic reads it for the compiled database). If the bundled files are absent
(e.g. a source run) the hook is a no-op and normal discovery applies.
"""

import os
import sys

if getattr(sys, "frozen", False):
    _base = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
    _dylib = os.path.join(_base, "libmagic.dylib")
    _mgc = os.path.join(_base, "magic.mgc")

    if os.path.exists(_mgc):
        os.environ.setdefault("MAGIC", _mgc)

    if os.path.exists(_dylib):
        import ctypes.util as _ctypes_util

        _orig_find_library = _ctypes_util.find_library

        def _find_library(name):
            if name in ("magic", "libmagic"):
                return _dylib
            return _orig_find_library(name)

        _ctypes_util.find_library = _find_library
