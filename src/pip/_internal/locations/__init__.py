import logging
import pathlib
import sysconfig
from typing import List, Optional

from pip._internal.models.scheme import SCHEME_KEYS, Scheme

from . import _distutils, _sysconfig
from .base import (
    USER_CACHE_DIR,
    get_bin_user,
    get_major_minor_version,
    get_src_prefix,
    site_packages,
    user_site,
)

__all__ = [
    "USER_CACHE_DIR",
    "get_bin_prefix",
    "get_bin_user",
    "get_major_minor_version",
    "get_platlib",
    "get_prefixed_libs",
    "get_purelib",
    "get_scheme",
    "get_src_prefix",
    "site_packages",
    "user_site",
]


logger = logging.getLogger(__name__)


def _default_base(*, user):
    # type: (bool) -> str
    if user:
        base = sysconfig.get_config_var("userbase")
    else:
        base = sysconfig.get_config_var("base")
    assert base is not None
    return base


def _warn_if_mismatch(old, new, *, key):
    # type: (pathlib.Path, pathlib.Path, str) -> None
    if old == new:
        return
    issue_url = "https://github.com/pypa/pip/issues/9617"
    message = (
        "Value for %s does not match. Please report this to %s"
        "\ndistutils: %s"
        "\nsysconfig: %s"
    )
    logger.warning(message, key, issue_url, old, new)


def get_scheme(
    dist_name,  # type: str
    user=False,  # type: bool
    home=None,  # type: Optional[str]
    root=None,  # type: Optional[str]
    isolated=False,  # type: bool
    prefix=None,  # type: Optional[str]
):
    # type: (...) -> Scheme
    old = _distutils.get_scheme(
        dist_name,
        user=user,
        home=home,
        root=root,
        isolated=isolated,
        prefix=prefix,
    )
    new = _sysconfig.get_scheme(
        dist_name,
        user=user,
        home=home,
        root=root,
        isolated=isolated,
        prefix=prefix,
    )

    base = prefix or home or _default_base(user=user)
    for k in SCHEME_KEYS:
        # Extra join because distutils can return relative paths.
        old_v = pathlib.Path(base, getattr(old, k))
        new_v = pathlib.Path(getattr(new, k))
        _warn_if_mismatch(old_v, new_v, key=f"scheme.{k}")

    return old


def get_bin_prefix():
    # type: () -> str
    old = _distutils.get_bin_prefix()
    new = _sysconfig.get_bin_prefix()
    _warn_if_mismatch(pathlib.Path(old), pathlib.Path(new), key="bin_prefix")
    return old


def get_purelib():
    # type: () -> str
    """Return the default pure-Python lib location."""
    old = _distutils.get_purelib()
    new = _sysconfig.get_purelib()
    _warn_if_mismatch(pathlib.Path(old), pathlib.Path(new), key="purelib")
    return old


def get_platlib():
    # type: () -> str
    """Return the default platform-shared lib location."""
    old = _distutils.get_platlib()
    new = _sysconfig.get_platlib()
    _warn_if_mismatch(pathlib.Path(old), pathlib.Path(new), key="platlib")
    return old


def get_prefixed_libs(prefix):
    # type: (str) -> List[str]
    """Return the lib locations under ``prefix``."""
    old_pure, old_plat = _distutils.get_prefixed_libs(prefix)
    new_pure, new_plat = _sysconfig.get_prefixed_libs(prefix)
    _warn_if_mismatch(
        pathlib.Path(old_pure),
        pathlib.Path(new_pure),
        key="prefixed-purelib",
    )
    _warn_if_mismatch(
        pathlib.Path(old_plat),
        pathlib.Path(new_plat),
        key="prefixed-platlib",
    )
    if old_pure == old_plat:
        return [old_pure]
    return [old_pure, old_plat]
