import sys
import os
from pathlib import Path

# Add src to Python path so `ideaos` imports resolve seamlessly
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from ideaos.main import app

# Expose app for Vercel / ASGI runners
__all__ = ["app"]
