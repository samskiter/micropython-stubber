# others
from typing import List
import pytest
from pathlib import Path

# SOT
from readfrom_rst import RSTReader, generate_from_rst

###################################################################################################
# Fixtures for re-use by different test methods
###################################################################################################

# TODO:
@pytest.fixture
def pyright(rst_stubs):
    "Run pyright over folder with rst generated stubs, and return the results"

    # cmd = ["pyright", "generated/micropython/1_16-nightly", "--outputjson"]
    cmd = ["pyright", rst_stubs.as_posix(), "--outputjson"]
    try:
        # result = subprocess.run(cmd, capture_output=False)
        result = subprocess.run(cmd, capture_output=True)
    except OSError as e:
        raise e
    results = json.loads(result.stdout)
    assert results["summary"]["filesAnalyzed"] >= 40, ">= 40 files checked"
    return results


@pytest.fixture
def rst_stubs(tmp_path):
    "Generate stubs from RST files"
    dst_folder = tmp_path
    rst_folder = Path("micropython/docs/library")
    v_tag = "v1_16"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=True)
    return tmp_path


###################################################################################################
#
###################################################################################################


def test_rst_all(tmp_path):
    v_tag = "v1_16"
    rst_folder = Path("micropython/docs/library")
    dst_folder = tmp_path / "noblack"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=False)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"

    dst_folder = tmp_path / "black"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=True)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"

    # rerun in same folder, same options
    dst_folder = tmp_path / "black"
    x = generate_from_rst(rst_folder, dst_folder, v_tag=v_tag, black=True)
    assert type(x) == int, "returns a number"
    assert x > 0, "should generate at least 1 file"


EXP_10 = ["def wake_on_ext0(pin, level) -> Any:", "def wake_on_ext0(pin, level) -> Any:"]


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("tests/rst_reader/data/function_10.rst", EXP_10),
        ("tests/rst_reader/data/function_11.rst", EXP_10),
        ("tests/rst_reader/data/function_12.rst", EXP_10),
        (
            "tests/rst_reader/data/function_12.rst",
            ["        Configure whether or not a touch will wake the device from sleep."],
        ),
    ],
)
def test_rst_parse_function(filename, expected):
    # testcase = FN_1
    r = RSTReader()
    r.read_file(filename)
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    for fn in expected:
        assert fn in [l.rstrip() for l in r.output]


CLASS_10 = [
    "class Partition:",
    "    def __init__(self, id) -> None:",
    "    @classmethod",
    "    def find(cls, type=TYPE_APP, subtype=0xff, label=None) -> Any:",
    #    "    def info(self, ) -> Any:",
    # "    def readblocks(self, block_num, buf) -> Any:",
    # "    def writeblocks(self, block_num, buf) -> Any:",
]


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("tests/rst_reader/data/class_10.rst", CLASS_10),
        ("tests/rst_reader/data/class_10.rst", ["    def info(self, ) -> Any:"]),
        (
            "tests/rst_reader/data/class_10.rst",
            ["    def readblocks(self, block_num, buf) -> Any:"],
        ),
    ],
)
def test_rst_parse_class(filename, expected):
    # testcase = FN_1
    r = RSTReader()
    r.read_file(filename)
    # process
    r.parse()
    # check
    assert len(r.output) > 1
    for line in expected:
        assert line in [l.rstrip() for l in r.output], f"did not generate : '{line}'"


@pytest.mark.parametrize(
    "param_in, param_out",
    [
        ("", ""),
        ("()", "()"),
        ("() :", "()"),  # aditional stuff
        ("(\\*, something)", "(*, something)"),  # wrong escaping
        ("([angle])", "(angle: Optional[Any])"),  # simple optional
        ("([angle, time=0])", "(angle: Optional[Any], time=0)"),  # dual optional - hardcoded
        ("('param')", "(param)"),
        ("(cert_reqs=CERT_NONE)", "(cert_reqs=None)"),
        (
            "(if_id=0, config=['dhcp' or configtuple])",
            "(if_id=0, config: Union[str,Tuple]='dhcp')",
        ),
        ("lambda)", "lambda_fn)"),
        # ("()", "()"),
        # ("()", "()"),
        # ("()", "()"),
        # ("()", "()"),
        # ("()", "()"),
    ],
)
def test_fix_param(param_in, param_out):
    r = RSTReader()
    result = r.fix_parameters(param_in)
    assert result == param_out


def test_import_typing():
    "always include typing"
    r = RSTReader()
    line = "from typing import Any, Optional, Union, Tuple"
    assert line in [l.rstrip() for l in r.output], f"did not import typing : '{line}'"


def test_fix_param_dynamic():
    r = RSTReader()

    # in 'machine' module

    param_in = "(*, trigger, handler=None, wake=machine.IDLE)"
    param_out = "(*, trigger, handler=None, wake=IDLE)"

    # in module
    r.current_module = "machine"
    result = r.fix_parameters(param_in)
    assert result == param_out

    r.current_module = ""
    result = r.fix_parameters(param_in)
    assert result != param_out
    assert result == param_in

    # -----------------------
    param_in = "baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=None, mosi=None, miso=None)"
    param_out = "baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=MSB, sck=None, mosi=None, miso=None)"

    # in class
    r.current_class = "SPI"
    result = r.fix_parameters(param_in)
    assert result == param_out
    # not in class
    r.current_class = ""
    result = r.fix_parameters(param_in)
    assert result != param_out
    assert result == param_in


import subprocess
import json


@pytest.mark.skip(reason="not strictly needed (yet)")
def test_undefined_variable(pyright, capsys):
    issues = pyright["generalDiagnostics"]
    issues = list(filter(lambda diag: diag["rule"] == "reportUndefinedVariable", issues))
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0, "there should be no type issues"


def test_invalid_strings(pyright, capsys):
    issues = pyright["generalDiagnostics"]

    # Only fail on errors
    issues = list(filter(lambda diag: diag["severity"] == "error", issues))
    issues = list(filter(lambda diag: diag["rule"] == "reportInvalidStringEscapeSequence", issues))
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    assert len(issues) == 0, "all string should be valid"


def test_obscured_definitions(pyright, capsys):
    issues = pyright["generalDiagnostics"]
    # Only look at errors
    issues = list(filter(lambda diag: diag["severity"] == "error", issues))
    issues = list(
        filter(
            lambda diag: diag["rule"] == "reportGeneralTypeIssues"
            and "is obscured by a declaration" in diag["message"],
            issues,
        )
    )
    with capsys.disabled():
        for issue in issues:
            print(f"{issue['message']} in {issue['file']} line {issue['range']['start']['line']}")
    # TODO:  ure.py 'Function declaration "match" is obscured by a declaration of the same name'
    assert len(issues) == 1, "no redefinitions that obscure earlier defs"


@pytest.mark.skip(reason="test not yet built")
def test_data_module_level():
    "all modules should have a docstring"
    ...


@pytest.mark.skip(reason="test not yet built")
def test_data_class_level():
    "all classes should have a docstring"
    ...


@pytest.mark.skip(reason="test not yet built")
def test_exception():
    # exception:: AssertionError
    ...


@pytest.mark.skip(reason="test not yet built")
def test_undocumented_class():
    ...


@pytest.mark.skip(reason="test not yet built")
def test_find_return_type():
    ...


@pytest.mark.skip(reason="test not yet built")
def test_dup_init():
    ...


# Duplicate __init__ FIXME: ucryptolib aes.__init__(key, mode, [IV])


@pytest.mark.skip(reason="test not yet built")
def test_deepsleep_stub():
    "Deepsleep stub is generated"
    file = list(rst_stubs.rglob("machine.py"))[0]
    if file:
        content = []
        with open(file) as f:
            content = f.readlines()
        found = any("def deepsleep(time_ms: Optional[Any]) -> Any:" in line for line in content)
        assert found, "usocket.socket should be stubbed as a class, not as a function"

    # # .. function:: deepsleep([time_ms])
    # def deepsleep(time_ms: Optional[Any]) -> Any:
    ...


@pytest.mark.skip(reason="test not yet built")
def test_Flash_init_overload():
    "pyb.Flash_init_overload is generated"
    # class Flash:
    #     """
    #     :noindex:
    #     Create and return a block device that accesses the flash at the specified offset. The length defaults to the remaining size of the device.
    #     The *start* and *len* offsets are in bytes, and must be a multiple of the block size (typically 512 for internal flash).
    #     """
    #     def __init__(self, *, start=-1, len=-1) -> None:
    ...


def test_usocket_class_def(rst_stubs: Path):
    "make sense of `usocket.socket` class documented as a function - Upstream Docfix pending"
    file = list(rst_stubs.rglob("usocket.py"))[0]
    if file:
        content = []
        with open(file) as f:
            content = f.readlines()
        found = any("def socket(" in line for line in content)
        assert not found, "usocket.socket should be stubbed as a class, not as a function"

        found = any("class socket:" in line for line in content)
        assert found, "usocket.socket classdef should be generated"

        found = any(
            "def __init__(self, af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP, /) -> None:"
            in line
            for line in content
        )
        assert found, "usocket.socket __init__ should be generated"


def test_poll_class_def(rst_stubs: Path):
    "make sense of `uselect.socket` class documented as a function - Upstream Docfix pending"
    file = list(rst_stubs.rglob("uselect.py"))[0]
    if file:
        content = []
        with open(file) as f:
            content = f.readlines()
        found = any("def poll()" in line for line in content)
        assert not found, "uselect.poll class should not be stubbed as a function"

        found = any("class poll:" in line for line in content)
        assert found, "uselect.poll should be stubbed as a class"


# def socket(af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP, /) -> Any:
