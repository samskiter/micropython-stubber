# others
import pytest
from helpers import load_rst

# SOT
from stubber.rst.reader import RSTWriter

# mark all tests
pytestmark = pytest.mark.doc_stubs


MACHINE_RST = """
:mod:`machine` --- functions related to the hardware
====================================================

.. module:: machine
   :synopsis: functions related to the hardware

The ``machine`` module contains specific functions related to the hardware

.. function:: rng()

   Return a 24-bit software generated random number.

   Availability: WiPy.

.. _machine_constants:

Constants
---------

.. data:: machine.IDLE
          machine.SLEEP
          machine.DEEPSLEEP

    IRQ wake values.

.. data:: machine.PWRON_RESET
          machine.HARD_RESET
          machine.WDT_RESET
          machine.DEEPSLEEP_RESET
          machine.SOFT_RESET

    Reset causes.

.. data:: machine.WLAN_WAKE
          machine.PIN_WAKE
          machine.RTC_WAKE

    Wake-up reasons.
"""

MACHINE_PIN_RST = """
Constructors
------------

.. class:: Pin(id, mode=-1, pull=-1, *, value, drive, alt)

   Access the pin peripheral (GPIO pin) associated with the given ``id``.  If
   additional arguments are given in the constructor then they are used to initialise
   the pin.  Any settings that are not specified will remain in their previous state.

Constants
---------

The following constants are used to configure the pin objects.  Note that
not all constants are available on all ports.

.. data:: Pin.IN
          Pin.OUT
          Pin.OPEN_DRAIN
          Pin.ALT
          Pin.ALT_OPEN_DRAIN

   Selects the pin mode.

.. data:: Pin.PULL_UP
          Pin.PULL_DOWN
          Pin.PULL_HOLD

   Selects whether there is a pull up/down resistor.  Use the value
   ``None`` for no pull.

.. data:: Pin.LOW_POWER
          Pin.MED_POWER
          Pin.HIGH_POWER

   Selects the pin drive strength.

.. data:: Pin.IRQ_FALLING
          Pin.IRQ_RISING
          Pin.IRQ_LOW_LEVEL
          Pin.IRQ_HIGH_LEVEL

   Selects the IRQ trigger type.

.. data:: Pin.JOKER_*

   Test wildcard handling.

"""


def test_module_constants():
    # test is module level constants can be processed
    r = RSTWriter()
    load_rst(r, MACHINE_RST)
    r.current_module = "machine"
    # process
    r.parse()
    r.prepare_output()
    # check
    assert len(r.output) > 1
    lst = r.output_dict["constants"]

    doc_list = [c for c in lst if c.startswith('"""')]
    const_list = [c for c in lst if not c.startswith('"""')]
    # should have 11  constants
    assert len(const_list) == 11
    # and 11 single line comments for docstrings
    assert len(doc_list) == 11


def test_class_constants():
    # check if the module name has been removed form the class def
    r = RSTWriter()
    load_rst(r, MACHINE_PIN_RST)
    # r.current_module = module # 'uhashlib'
    # process
    r.parse()
    r.prepare_output()
    # check
    assert len(r.output) > 1
    expected = [
        "class Pin():",
        "    IN: Incomplete",
        "    OUT: Incomplete",
        '    """Selects the pin mode."""',
        "    OPEN_DRAIN: Incomplete",
        "    ALT: Incomplete",
        '    """\\',
        "    Selects whether there is a pull up/down resistor.  Use the value",
        "    ``None`` for no pull.",
        '    """',
        "    # JOKER_*: Incomplete",
        '    """Test wildcard handling."""',
    ]
    lines = [l.rstrip() for l in r.output]
    for l in expected:
        assert l in lines, f"{l} not found"


def test_timer_constants(pytestconfig: pytest.Config):
    """
        2. the description of constants in not picked up correctly ( for the last one in a .rst file ?)
    rst
    Constants
    Timer.ONE_SHOT
    Timer.PERIODIC
    Timer operating mode.
    """
    r = RSTWriter()

    r.read_file(pytestconfig.rootpath / "tests/rst/data/machine.Timer.rst")
    r.current_module = "machine"
    # process
    r.parse()
    r.prepare_output()
    # check
    assert len(r.output) > 1
    lst = r.output_dict["class Timer():"]["constants"]

    doc_list = [c for c in lst if c.lstrip().startswith('"""')]
    const_list = [c for c in lst if not c.lstrip().startswith('"""')]
    # should have 2 constants
    assert len(const_list) == 2
    # and 11 single line comments for docstrings
    assert len(doc_list) == 2
    assert '    """Timer operating mode."""' in doc_list
