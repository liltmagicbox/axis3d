"""Shared pytest setup: GPU tests run only when AXIS3D_GPU=1 (needs a GL 4.6 window)."""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("AXIS3D_GPU") == "1":
        return
    skip = pytest.mark.skip(reason="GPU test: set AXIS3D_GPU=1 on a machine with a GL 4.6 display")
    for item in items:
        if "gpu" in item.keywords:
            item.add_marker(skip)
