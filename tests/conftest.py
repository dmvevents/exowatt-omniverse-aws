"""pytest bootstrap: make the offline harness importable, keep it offline.

The harness modules (quota_check, provision_g6e, omniverse_setup, first_scene,
selftest) are run as scripts from the harness/ directory (see the Makefile and
selftest.py), so they import one another by bare name. Put harness/ and the
repo root on sys.path so the tests import them exactly as the harness does.

No fixtures perform I/O or AWS calls; every test that touches the live boto3
path injects a mock into sys.modules, so the suite never contacts AWS.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_HARNESS = os.path.join(_ROOT, "harness")

for _p in (_HARNESS, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
