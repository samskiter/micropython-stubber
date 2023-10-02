import shutil
import subprocess
from pathlib import Path

import pytest
from loguru import logger as log


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if report.when == "call" and report.failed:
        # add the caplog errors and warnings to the report
        if not "caplog" in item.funcargs:
            return
        caplog = item.funcargs["caplog"]
        report_txt = (
            "\n"
            + "\n".join([r.message for r in caplog.records])
            + "\n\n"
            + str(report.longreprtext)
        )
        report.longrepr = report_txt

        return report


@pytest.fixture(scope="session")
def type_stub_cache_path(
    portboard: str,
    version: str,
    stub_source: str,
    pytestconfig: pytest.Config,
) -> Path:
    """
    Installs a copy of the type stubs for the given portboard and version.
    Returns the path to the cache folder
    """

    log.trace(f"setup install type_stubs to cache: {stub_source}, {version}, {portboard}")
    flatversion = version.replace(".", "_")
    cache_path = pytestconfig.rootpath / "snippets" / "typings_cache"
    tsc_path = cache_path / f"typings_{flatversion}_{portboard}_stub_{stub_source}"
    # clean up prior
    if tsc_path.exists():
        shutil.rmtree(tsc_path, ignore_errors=True)
    # use pip to install type stubs
    # Install type stubs for portboard and version
    if stub_source == "pypi":
        # Add version
        cmd = f"pip install micropython-{portboard}-stubs=={version.lower().lstrip('v')}.* --target {tsc_path} --no-user"
    else:
        foldername = f"micropython-{flatversion}-{portboard}-stubs"
        stubsource = pytestconfig.rootpath / f"repos/micropython-stubs/publish/{foldername}"
        cmd = f"pip install {stubsource} --target {tsc_path} --no-user"
    try:
        subprocess.run(cmd, shell=False, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # skip test if source connot be found
        print(f"{e.stderr}")
        pytest.skip(f"{e.stderr}")
    #
    return tsc_path


@pytest.fixture(scope="function")
def snip_path(feature: str, pytestconfig) -> Path:
    snip_path = pytestconfig.rootpath / "snippets" / f"feat_{feature}"
    if not snip_path.exists():
        snip_path = pytestconfig.rootpath / "snippets" / f"check_{feature}"
    return snip_path


@pytest.fixture(scope="function")
def copy_type_stubs(
    portboard: str, version: str, feature: str, type_stub_cache_path: Path, snip_path: Path
):
    """
    Copies installed/cached typestub fom cache to the feature folder
    """
    log.trace(f"- copy_type_stubs: {version}, {portboard} to {feature}")
    print(f"\n - copy_type_stubs : {version}, {portboard} to {feature}")
    if not snip_path or not snip_path.exists():
        # skip if no feature folder
        pytest.skip(f"no feature folder for {feature}")
    typings_path = snip_path / "typings"
    if typings_path.exists():
        shutil.rmtree(typings_path, ignore_errors=True)
    shutil.copytree(type_stub_cache_path, typings_path)
    # time.sleep(0.2)
