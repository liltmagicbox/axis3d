"""Smoke: the package imports and reports a version."""

import axis3d


def test_package_has_version():
    # importing the package must not need a window, a GPU, or any GL call
    assert axis3d.__version__
