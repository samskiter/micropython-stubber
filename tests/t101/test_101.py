##########################

import version

##########################


def test_minified(mock_micropython_path, add_minified_path):
    from createstubs import __version__ as version  # type: ignore

    assert version


def test_version():
    assert version.VERSION


def test_dummy():
    assert True


def test_foo(pytestconfig, testrepo_micropython):
    if pytestconfig.getoption("verbose") > 0:
        assert 1