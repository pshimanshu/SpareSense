"""
FinWise backend package.

This file ensures `backend.app` is treated as a regular Python package so
intra-package imports (e.g. `from .ai.router import router`) work reliably.
"""

import warnings

# Silence noisy SSL backend warning from urllib3 on macOS system Python.
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL*", category=Warning)
