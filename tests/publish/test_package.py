import shutil
from pathlib import Path

import pytest
import stubber.publish.stubpacker as stubpacker
from stubber.publish.publish_stubs import (ALL_TYPES, COMBO_STUBS, CORE_STUBS,
                                           DOC_STUBS, create_package,
                                           get_package_info, package_name)

# # use our test paths
# stubpacker.PUBLISH_PATH = Path("./scratch/publish")
# stubpacker.TEMPLATE_PATH = Path("./tests/publish/data/template")
# stubpacker.STUB_PATH = Path("./all-stubs")


# test generation of different package names
@pytest.mark.parametrize(
    "family, pkg, port, board, expected",
    [
        ("micropython", COMBO_STUBS, "esp32", "GENERIC", "micropython-esp32-stubs"),
        ("micropython", COMBO_STUBS, "esp32", "TINY", "micropython-esp32-tiny-stubs"),
        ("micropython", DOC_STUBS, "esp32", None, "micropython-doc-stubs"),
        ("micropython", DOC_STUBS, "esp32", "GENERIC", "micropython-doc-stubs"),
        ("micropython", CORE_STUBS, None, None, "micropython-core-stubs"),
        ("micropython", CORE_STUBS, None, None, "micropython-core-stubs"),
        ("pycom", CORE_STUBS, None, None, "pycom-core-stubs"),
    ],
)
def test_package_name(family, pkg, port, board, expected):
    x = package_name(family=family, pkg_type=pkg, port=port, board=board)
    assert x == expected


# test creating a DOC_STUBS package
@pytest.mark.parametrize(
    "pkg_type, port, board",
    [
        (DOC_STUBS, None, None),
        (COMBO_STUBS, "esp32", "GENERIC"),
    ],
)
# CORE_STUBS
def test_create_package(tmp_path, pytestconfig, pkg_type, port, board, mocker):
    """ "
    test Create a new package with the DOC_STUBS type
    - test the different methods to manipulate the package on disk
    """

    PUBLISH_PATH = tmp_path / "publish"
    PUBLISH_PATH.mkdir(parents=True)

    # TODO: need to ensure that the stubs are avaialble in GHA testing
    STUB_PATH = Path("./repos/micropython-stubs/stubs")
    TEMPLATE_PATH = pytestconfig.rootpath / "tests/publish/data/template"

    mocker.patch("stubber.publish.stubpacker.STUB_PATH", STUB_PATH)
    mocker.patch("stubber.publish.stubpacker.TEMPLATE_PATH", TEMPLATE_PATH)
    mocker.patch("stubber.publish.stubpacker.PUBLISH_PATH", PUBLISH_PATH)

    # copy test data ?
    source = pytestconfig.rootpath / "tests/publish/data"
    #    shutil.copytree(source, PUBLISH_PATH)

    mpy_version = "v1.18"
    family = "micropython"
    pkg_name = f"foobar-{pkg_type}-stubs"

    package = create_package(
        pkg_name,
        mpy_version=mpy_version,
        family=family,
        port=port,
        board=board,
        pkg_type=pkg_type,
        # stub_source="./all-stubs",  # for debugging
    )
    assert isinstance(package, stubpacker.StubPackage)
    run_common_package_tests(package, pkg_name, publish_path=PUBLISH_PATH, stub_path=STUB_PATH, pkg_type=pkg_type)


read_db_data = [
    {
        "name": "foo-bar-stubs",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "foo-v1_18-bar-stubs",
        "stub_sources": [
            ["Firmware stubs", "micropython-v1_17-stm32"],
            ["Frozen stubs", "micropython-v1_17-frozen/stm32/GENERIC"],
            ["Core Stubs", "cpython_core-pycopy"],
        ],
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
    },
    {
        "name": "foo-bar-stubs",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "foo-v1_18-bar-stubs",
        "stub_sources": [
            ["Firmware stubs", "stubs/micropython-v1_17-stm32"],
            ["Frozen stubs", "stubs/micropython-v1_17-frozen/stm32/GENERIC"],
            ["Core Stubs", "stubs/cpython_core-pycopy"],
        ],
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
    },
    {
        "name": "foo-bar-stubs",
        "mpy_version": "1.18",
        "publish": True,
        "pkg_version": "1.18.post6",
        "path": "publish/foo-v1_18-bar-stubs",
        "stub_sources": [
            ["Firmware stubs", "micropython-v1_17-stm32"],
        ],
        "description": "foo bar stubs",
        "hash": "b09f9c819c9e98cbd9dfbc8158079146587e2d66",
    },
]


@pytest.mark.parametrize("json", read_db_data)
def test_package_from_json(tmp_path, pytestconfig, mocker, json):
    # test data
    source = pytestconfig.rootpath / "tests/publish/data"
    PUBLISH_PATH = tmp_path / "publish"
    PUBLISH_PATH.mkdir(parents=True)

    # TODO: need to ensure that the stubs are avaialble in GHA testing
    STUB_PATH = Path("./repos/micropython-stubs/stubs")
    TEMPLATE_PATH = pytestconfig.rootpath / "tests/publish/data/template"

    mocker.patch("stubber.publish.stubpacker.STUB_PATH", STUB_PATH)
    mocker.patch("stubber.publish.stubpacker.TEMPLATE_PATH", TEMPLATE_PATH)
    mocker.patch("stubber.publish.stubpacker.PUBLISH_PATH", PUBLISH_PATH)

    mpy_version = "v1.18"
    family = "micropython"
    pkg_name = "foo-bar-stubs"
    # todo: include stubs in the test data
    # note uses `stubs` relative to the stubs_folder

    package = stubpacker.StubPackage(pkg_name, version=mpy_version, json_data=json)
    assert isinstance(package, stubpacker.StubPackage)
    run_common_package_tests(package, pkg_name, PUBLISH_PATH, stub_path=STUB_PATH, pkg_type=None)


def run_common_package_tests(package, pkg_name, publish_path: Path, stub_path: Path, pkg_type):
    "a series of tests to re-use for all packages"
    assert isinstance(package, stubpacker.StubPackage)
    assert package.package_name == pkg_name

    assert package.package_path.relative_to(publish_path), "package path should be relative to publish path"
    assert (package.package_path).exists()
    assert (package.package_path / "pyproject.toml").exists()

    assert len(package.stub_sources) >= 1
    for s in package.stub_sources:
        folder = stub_path / s[1]
        assert folder.is_dir(), "stub source should be folder"
        assert folder.exists(), "stubs source should exists"
    #        assert not s[1].is_absolute(), "should be a relative path"
    # update existing pyproject.toml
    package.create_update_pyproject_toml()
    assert (package.package_path / "pyproject.toml").exists()

    package.create_readme()
    assert (package.package_path / "README.md").exists()
    package.create_license()
    assert (package.package_path / "LICENSE.md").exists()
    package.copy_stubs()
    filelist = list((package.package_path).rglob("*.py")) + list((package.package_path).rglob("*.pyi"))
    assert len(filelist) >= 1

    # do it all at once
    package.update_package_files()
    filelist = list((package.package_path).rglob("*.py")) + list((package.package_path).rglob("*.pyi"))
    assert len(filelist) >= 1

    package.update_included_stubs()
    stubs_in_pkg = package.pyproject["tool"]["poetry"]["packages"]  # type: ignore
    assert len(stubs_in_pkg) >= 1

    hash = package.create_hash()
    assert isinstance(hash, str)
    assert len(hash) > 30  # 41 bytes ?

    assert package.is_changed() == True

    result = package.check()
    assert result == True

    new_version = package.bump()
    assert new_version
    assert isinstance(new_version, stubpacker.Version)

    built = package.build()
    assert built
    assert (package.package_path / "dist").exists(), "Distribution folder should exist"
    filelist = list((package.package_path / "dist").glob("*.whl")) + list((package.package_path / "dist").glob("*.tar.gz"))
    assert len(filelist) >= 2

    package.clean()
    filelist = list((package.package_path).rglob("*.py")) + list((package.package_path).rglob("*.pyi"))
    assert len(filelist) == 0
