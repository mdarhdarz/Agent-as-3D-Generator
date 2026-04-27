# Copyright (C) 2023, Princeton University.

# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory
# of this source tree.

import logging
import os
import sys
from pathlib import Path

__version__ = "1.19.1"


def _enable_local_shims():
    shim_dir = Path(__file__).parent.parent / "__codex_shims__"
    if not shim_dir.is_dir():
        return

    shim_setting = os.environ.get("INFINIGEN_ENABLE_CODEX_SHIMS")
    if shim_setting == "0":
        return

    if shim_setting != "1":
        try:
            import numpy as np
        except Exception:
            return

        if int(np.__version__.split(".", 1)[0]) < 2:
            return

    shim_dir_str = str(shim_dir)
    if shim_dir_str not in sys.path:
        sys.path.insert(0, shim_dir_str)


_enable_local_shims()


def repo_root():
    return Path(__file__).parent.parent
