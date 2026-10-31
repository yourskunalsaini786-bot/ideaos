import sys
import os
from pathlib import Path

# Add apps/api/src to Python path so `ideaos` package can be imported seamlessly
root_dir = Path(__file__).resolve().parent.parent
api_src = root_dir / "apps" / "api" / "src"
if str(api_src) not in sys.path:
    sys.path.insert(0, str(api_src))

from ideaos.main import app

__all__ = ["app"]
