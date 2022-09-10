from typing import Optional

from packaging.version import Version, parse
from pypi_simple import PyPISimple
from stubber.utils.config import CONFIG


def get_pypy_versions( package_name:str, base : Optional[Version] = None, production:bool = True):
    """Get all versions of a package from a PyPI endpoint."""
    package_info = None
    if production:
        endpoint = "https://pypi.org/simple/"
    else:
        endpoint = "https://test.pypi.org/simple/"

    with PyPISimple(endpoint = endpoint) as client:
        package_info = client.get_project_page(project = package_name)

    if not package_info:
        return []

    versions = [parse(pkg.version) for pkg in package_info.packages if pkg.package_type == 'wheel' and pkg.version]
    # print(versions)

    if base:
        # if base provided then filter
        versions = [v for v in versions if v.base_version == base.base_version]

    return sorted(versions)