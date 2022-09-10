from pathlib import Path
from typing import List

import pytest

# module under test :
import stubber.stubber as stubber
from click.testing import CliRunner
from mock import MagicMock
from pytest_mock import MockerFixture
from stubber.commands.switch import VERSION_LIST

# mark all tests
pytestmark = pytest.mark.cli


def test_stubber_help():
    # check basic commandline sanity check
    runner = CliRunner()
    result = runner.invoke(stubber.stubber_cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Commands:" in result.output


##########################################################################################
# clone
##########################################################################################
def test_stubber_clone(mocker: MockerFixture, tmp_path: Path):
    runner = CliRunner()
    # from stubber.commands.clone import git
    m_clone: MagicMock = mocker.patch("stubber.commands.clone.git.clone", autospec=True, return_value=0)
    m_fetch: MagicMock = mocker.patch("stubber.commands.clone.git.fetch", autospec=True, return_value=0)
    result = runner.invoke(stubber.stubber_cli, ["clone"])
    assert result.exit_code == 0

    # either clone or fetch
    assert m_clone.call_count + m_fetch.call_count == 2
    if m_clone.call_count > 0:
        m_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython.git", path=Path("repos/micropython"))
        m_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython-lib.git", path=Path("repos/micropython-lib"))
    else:
        m_fetch.assert_any_call(Path("repos/micropython"))
        m_fetch.assert_any_call(Path("repos/micropython-lib"))


def test_stubber_clone_path(mocker: MockerFixture, tmp_path: Path):
    runner = CliRunner()
    m_clone: MagicMock = mocker.patch("stubber.commands.clone.git.clone", autospec=True, return_value=0)

    m_tag = mocker.patch("stubber.commands.clone.git.get_tag", autospec=True)
    m_dir = mocker.patch("stubber.commands.clone.os.mkdir", autospec=True)

    # now test with path specified
    result = runner.invoke(stubber.stubber_cli, ["clone", "--path", "foobar"])
    assert result.exit_code == 0

    assert m_clone.call_count >= 2
    m_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython.git", path=Path("foobar/micropython"))
    m_clone.assert_any_call(remote_repo="https://github.com/micropython/micropython-lib.git", path=Path("foobar/micropython-lib"))
    assert m_tag.call_count >= 2


##########################################################################################
# switch
##########################################################################################


@pytest.mark.parametrize(
    "params",
    [
        pytest.param(["switch", "--version", "latest", "--path", "foobar"], id="latest"),
        pytest.param(["switch", "--version", "v1.9.4", "--path", "foobar"], id="v1.9.4"),
    ],
)
def test_stubber_switch(mocker: MockerFixture, params: List[str]):
    runner = CliRunner()
    # Mock Path.exists
    m_clone: MagicMock = mocker.patch("stubber.commands.clone.git.clone", autospec=True, return_value=0)
    m_fetch: MagicMock = mocker.patch("stubber.commands.clone.git.fetch", autospec=True, return_value=0)

    m_switch: MagicMock = mocker.patch("stubber.commands.clone.git.switch_branch", autospec=True, return_value=0)
    m_checkout: MagicMock = mocker.patch("stubber.commands.clone.git.checkout_tag", autospec=True, return_value=0)
    m_get_tag: MagicMock = mocker.patch("stubber.commands.clone.git.get_tag", autospec=True, return_value="v1.42")

    m_match = mocker.patch("stubber.get_mpy.match_lib_with_mpy", autospec=True)

    m_exists = mocker.patch("stubber.commands.clone.Path.exists", return_value=True)
    result = runner.invoke(stubber.stubber_cli, params)
    assert result.exit_code == 0

    # fetch latest
    assert m_fetch.call_count == 2
    # "foobar" from params is used as the path
    m_fetch.assert_any_call(Path("foobar/micropython"))
    m_fetch.assert_any_call(Path("foobar/micropython-lib"))

    # core
    m_match.assert_called_once()

    if "latest" in params:
        m_switch.assert_called_once()
        m_checkout.assert_not_called()
    else:
        m_switch.assert_not_called()
        m_checkout.assert_called_once()


@pytest.mark.parametrize("version", VERSION_LIST)
def test_stubber_switch_version(mocker: MockerFixture, version: str):
    runner = CliRunner()
    # Mock Path.exists
    m_clone: MagicMock = mocker.patch("stubber.commands.clone.git.clone", autospec=True, return_value=0)
    m_fetch: MagicMock = mocker.patch("stubber.commands.clone.git.fetch", autospec=True, return_value=0)

    m_switch: MagicMock = mocker.patch("stubber.commands.clone.git.switch_branch", autospec=True, return_value=0)
    m_checkout: MagicMock = mocker.patch("stubber.commands.clone.git.checkout_tag", autospec=True, return_value=0)
    m_get_tag: MagicMock = mocker.patch("stubber.commands.clone.git.get_tag", autospec=True, return_value="v1.42")

    m_match = mocker.patch("stubber.get_mpy.match_lib_with_mpy", autospec=True)

    m_exists = mocker.patch("stubber.commands.clone.Path.exists", return_value=True)
    result = runner.invoke(stubber.stubber_cli, ["switch", "--version", version])
    assert result.exit_code == 0

    # fetch latest
    assert m_fetch.call_count == 2
    # "foobar" from params is used as the path
    m_fetch.assert_any_call(Path("repos/micropython"))
    m_fetch.assert_any_call(Path("repos/micropython-lib"))


##########################################################################################
# minify
##########################################################################################
def test_stubber_minify(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock_minify: MagicMock = mocker.MagicMock(return_value=0)
    mocker.patch("stubber.commands.minify.minify", mock_minify)

    result = runner.invoke(stubber.stubber_cli, ["minify"])
    assert result.exit_code == 0
    mock_minify.assert_called_once_with("board/createstubs.py", "./minified", True, False, False)


def test_stubber_minify_all(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    mock_minify: MagicMock = mocker.MagicMock(return_value=0)
    mocker.patch("stubber.commands.minify.minify", mock_minify)

    result = runner.invoke(stubber.stubber_cli, ["minify", "--all"])
    assert result.exit_code == 0
    assert mock_minify.call_count == 3
    mock_minify.assert_any_call("board/createstubs.py", "./minified", True, False, False)
    mock_minify.assert_any_call("board/createstubs_db.py", "./minified", True, False, False)
    mock_minify.assert_any_call("board/createstubs_mem.py", "./minified", True, False, False)


##########################################################################################
# stub
##########################################################################################
def test_stubber_stub(mocker: MockerFixture):
    # check basic commandline sanity check
    runner = CliRunner()
    # mock: MagicMock = mocker.MagicMock(return_value=True)
    mock: MagicMock = mocker.patch("stubber.utils.generate_pyi_files", autospec=True, return_value=True)
    # fake run on current folder
    result = runner.invoke(stubber.stubber_cli, ["stub", "--source", "."])

    mock.assert_called_once_with(Path("."))
    assert result.exit_code == 0


##########################################################################################
# get-frozen
##########################################################################################


def test_stubber_get_frozen(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock_version: MagicMock = mocker.patch("stubber.basicgit.get_tag", autospec=True, return_value="v1.42")

    mock: MagicMock = mocker.patch("stubber.get_mpy.get_frozen", autospec=True)
    mock_post: MagicMock = mocker.patch("stubber.utils.do_post_processing", autospec=True)

    # fake run - need to ensure that there is a destination folder
    result = runner.invoke(stubber.stubber_cli, ["get-frozen", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # FIXME : test failes in CI
    mock.assert_called_once()
    mock_version.assert_called_once()

    mock_post.assert_called_once_with([tmp_path / "micropython-v1_42-frozen"], True, True)


##########################################################################################
# get-lobo
##########################################################################################
def test_stubber_get_lobo(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock: MagicMock = mocker.patch("stubber.get_lobo.get_frozen", autospec=True)
    mock_post: MagicMock = mocker.patch("stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-lobo", "--stub-folder", tmp_path.as_posix()])
    mock.assert_called_once()
    mock_post.assert_called_once()
    mock_post.assert_called_once_with([tmp_path / "loboris-v3_2_24-frozen"], True, True)
    assert result.exit_code == 0


##########################################################################################
# get-core
##########################################################################################


def test_stubber_get_core(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()
    mock: MagicMock = mocker.patch("stubber.get_cpython.get_core", autospec=True)
    mock_post: MagicMock = mocker.patch("stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-core", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # process is called twice
    assert mock.call_count == 2

    # post is called one
    mock_post.assert_called_with([tmp_path / "cpython_core-pycopy", tmp_path / "cpython_core-micropython"], True, True)


##########################################################################################
# get-docstubs
##########################################################################################


def test_stubber_get_docstubs(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock_version: MagicMock = mocker.patch("stubber.basicgit.get_tag", autospec=True, return_value="v1.42")

    # from stubber.commands.get_docstubs import generate_from_rst
    mock: MagicMock = mocker.patch("stubber.commands.get_docstubs.generate_from_rst", autospec=True)

    mock_post: MagicMock = mocker.patch("stubber.utils.do_post_processing", autospec=True)

    # fake run
    result = runner.invoke(stubber.stubber_cli, ["get-docstubs", "--stub-folder", tmp_path.as_posix()])
    assert result.exit_code == 0
    # process is called twice
    assert mock.call_count == 1
    mock.assert_called_once()
    assert mock_version.call_count >= 1

    # post is called one
    mock_post.assert_called_with([tmp_path / "micropython-v1_42-docstubs"], False, True)


##########################################################################################
# get-lobo
##########################################################################################
def test_stubber_fallback(mocker: MockerFixture, tmp_path: Path):
    # check basic commandline sanity check
    runner = CliRunner()

    mock: MagicMock = mocker.patch("stubber.commands.update_fallback.update_fallback", autospec=True)
    # mock2: MagicMock = mocker.patch("stubber.update_fallback.update_fallback", autospec=True)
    # from .update_fallback import update_fallback,
    # fake run
    result = runner.invoke(stubber.stubber_cli, ["update-fallback", "--stub-folder", tmp_path.as_posix()])
    mock.assert_called_once()
    assert result.exit_code == 0
