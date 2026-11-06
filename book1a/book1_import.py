"""Import the frozen Book 1 engine (read-only reference copy in book1_ref/) as `jeron_engine`.

Book 1A never edits it. On the PC, set BOOK1_ROOT to K:\\Databento_BackTesting (the tagged checkout);
here it defaults to the byte-exact Drive mirror in book1_ref/.
"""
import os
import sys
from pathlib import Path

BOOK1_ROOT = Path(os.environ.get("BOOK1_ROOT", Path(__file__).resolve().parent.parent / "book1_ref"))
if str(BOOK1_ROOT) not in sys.path:
    sys.path.insert(0, str(BOOK1_ROOT))

import jeron_engine  # noqa: E402
from jeron_engine import fills  # noqa: E402

__all__ = ["BOOK1_ROOT", "jeron_engine", "fills"]
