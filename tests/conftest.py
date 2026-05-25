import sys
import os

_SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'skills'))

def pytest_pycollect_makemodule(module_path, parent):
    """Isolate each skill test by cleaning up sys.path and sys.modules from previous skill imports."""
    # Remove previously added skill paths from sys.path
    sys.path[:] = [p for p in sys.path if not p.startswith(_SKILLS_DIR)]
    # Clear 'scripts' namespace to avoid cross-skill module collisions
    to_remove = [k for k in sys.modules if k == "scripts" or k.startswith("scripts.")]
    for k in to_remove:
        del sys.modules[k]
