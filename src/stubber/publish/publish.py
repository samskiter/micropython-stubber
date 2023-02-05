"""
prepare a set of stub files for publishing to PyPi

!!Note: anything excluded in .gitignore is not packaged by poetry
"""
from typing import Any, Dict, List
from loguru import logger as log

from stubber.publish.candidates import board_candidates, is_auto
from stubber.publish.database import get_database
from stubber.publish.enums import COMBO_STUBS
from stubber.publish.package import get_package
from stubber.utils.config import CONFIG
from stubber.publish.package import GENERIC

def build_multiple(
    family: str = "micropython",
    versions: List[str] = ["v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = [GENERIC],
    production: bool = False,
    clean: bool = False,
    force: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Build a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)
    results:List[Dict[str, Any]] = []
    worklist = build_worklist(family, versions, ports, boards)
    if len(worklist) == 0:
        log.error("Could not find any packages than can be build.")
        return results
    log.info(f"checking {len(worklist)} possible board candidates")

    for todo in worklist:
        if package := get_package(db, **todo):
            package.build(force=force, production=production)
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def publish_multiple(
    family: str = "micropython",
    versions: List[str] = ["v1.19.1"],
    ports: List[str] = ["auto"],
    boards: List[str] = [GENERIC],
    production: bool = False,
    clean: bool = False,
    build: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:  # sourcery skip: default-mutable-arg
    """
    Publish a bunch of stub packages
    """
    db = get_database(CONFIG.publish_path, production=production)
    results = []
    worklist = build_worklist(family, versions, ports, boards)

    if len(worklist) == 0:
        log.error("Could not find any packages than can be published.")
        return results

    for todo in worklist:
        if package := get_package(db, **todo):
            package.publish(db=db, clean=clean, force=force, build=build, production=production, dry_run=dry_run)
            results.append(package.status)
        else:
            log.error(f"Failed to create package for {todo}")
    return results


def build_worklist(family: str, versions: List[str], ports: List[str], boards: List[str]):
    """Build a worklist of packages to build or publish, and filter to only the requested ports and boards"""
    if isinstance(versions, str):
        versions = [versions]
    if isinstance(ports, str):
        ports = [ports]
    if isinstance(boards, str):
        boards = [boards]
    if family != "micropython":
        return []
    # get all the candidates
    worklist = list(board_candidates(family=family, versions=versions, pt=COMBO_STUBS))
    worklist = [i for i in worklist if i["board"] != ""]
    # then filter down to the ones we want
    if not is_auto(ports):
        ports_ = [i.lower() for i in ports]
        worklist = [i for i in worklist if i["port"].lower() in ports_]
    if not is_auto(boards):
        boards_ = [i.lower() for i in boards]
        worklist = [i for i in worklist if i["board"].lower() in boards_]

    for b in boards:
        if not any(i for i in worklist if i["board"] == b):
            log.warning(f"Could not find any package candidate for board {b}")
    return worklist
