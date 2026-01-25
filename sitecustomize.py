"""
Repo-local Python startup tweaks.

Python automatically imports `sitecustomize` (if present on sys.path) during
startup. We use this to silence noisy, non-actionable warnings that otherwise
clutter hackathon demo output.
"""

import warnings

# macOS system Python may be linked against LibreSSL, which triggers this warning
# when urllib3 v2 is imported (via requests). It is safe to ignore for this project.
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL*", category=Warning)

