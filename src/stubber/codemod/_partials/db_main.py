"""
This file contains the `def main()` funcion for the db variant of createstubs.py
- type_check_only is used to avoid circular imports
The partial is enclosed in ###PARTIAL### and ###PARTIALEND### markers
"""

from typing import TYPE_CHECKING, List, type_check_only

if TYPE_CHECKING:
    import sys
    from logging import Logger

    @type_check_only
    class Stubber:
        path: str
        _report: List[str]
        modules = []

        def __init__(self, path: str = "", firmware_id: str = "") -> None:
            ...

        def clean(self) -> None:
            ...

        def create_one_stub(self, modulename: str) -> bool:
            ...

        def report(self, filename: str = "modules.json"):
            ...

        def create_all_stubs(self):
            ...

    @type_check_only
    def read_path() -> str:
        ...

    @type_check_only
    class _gc:
        def collect(self) -> None:
            ...

    gc: _gc
    _log: Logger


###PARTIAL###
def main():
    import machine  # type: ignore

    try:
        f = open("modulelist" + ".done", "r+b")
        was_running = True
        _log.info("Opened existing db")
    except OSError:
        f = open("modulelist" + ".done", "w+b")
        _log.info("created new db")
        was_running = False

    stubber = Stubber(path=read_path())
    if not was_running:
        # Only clean folder if this is a first run
        stubber.clean()

    # get list of modules to process
    stubber.modules = ["micropython"]
    for p in ["", "/libs"]:
        try:
            with open(p + "modulelist" + ".txt") as f:
                # not optimal , but works on mpremote and eps8266
                stubber.modules = [l.strip() for l in f.read().split("\n") if len(l.strip()) and l.strip()[0] != "#"]
                break
        except OSError:
            pass
    gc.collect()
    # remove the ones that are already done
    modules_done = {}  # type: dict[str, str]
    try:
        with open("modulelist" + ".done") as f:
            # not optimal , but works on mpremote and esp8266
            for line in f.read().split("\n"):
                line = line.strip()
                gc.collect()
                if len(line) > 0:
                    key, value = line.split("=", 1)
                    modules_done[key] = value
    except (OSError, SyntaxError):
        pass
    gc.collect()
    # see if we can continue from where we left off
    modules = [m for m in stubber.modules if m not in modules_done.keys()]
    gc.collect()

    for modulename in modules:
        # ------------------------------------
        # do epic shit
        # but sometimes things fail
        ok = False
        try:
            ok = stubber.create_one_stub(modulename)
        except MemoryError:
            # RESET AND HOPE THAT IN THE NEXT CYCLE WE PROGRESS FURTHER
            machine.reset()

        # save the (last) result back to the database/result file
        result = stubber._report[-1] if ok else "failed"
        # -------------------------------------
        modules_done[modulename] = str(result)
        with open("modulelist" + ".done", "a") as f:
            f.write("{}={}\n".format(modulename, result))

    # Finished processing - load all the results , and remove the failed ones
    if modules_done:
        stubber._report = [v for _, v in modules_done.items() if v != "failed"]
        stubber.report()


###PARTIALEND###