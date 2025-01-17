"""partial used to read the modulelist.txt file"""
from typing import TYPE_CHECKING, List, type_check_only

if TYPE_CHECKING:
    import gc
    import logging

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

    _log = logging.getLogger("stubber")

    # help type checker
    stubber: Stubber = None  # type: ignore
    LIBS: List[str] = [".", "lib"]

# sourcery skip: use-named-expression
###PARTIAL###
# Read stubs from modulelist in the current folder or in /libs
# fall back to default modules
stubber.modules = []  # avoid duplicates
for p in LIBS:
    try:
        _1 = gc.mem_free()  # type: ignore
        with open(p + "/modulelist.txt") as f:
            print("Debug: List of modules: " + p + "/modulelist.txt")
            line = f.readline()
            while line:
                line = line.strip()
                if len(line) > 0 and line[0] != "#":
                    stubber.modules.append(line)
                line = f.readline()
            gc.collect()  # type: ignore
            print("Debug: Used memory to load modulelist.txt: " + str(_1 - gc.mem_free()) + " bytes")  # type: ignore
            break
    except Exception:
        pass
if not stubber.modules:
    stubber.modules = ["micropython"]
    print("Could not find modulelist.txt, using default modules")
###PARTIALEND###
