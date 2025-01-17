""" 
Merge firmware stubs and docstubs into a single folder
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union

from loguru import logger as log

from stubber.codemod.enrich import enrich_folder
from stubber.publish.candidates import board_candidates, filter_list
from stubber.publish.missing_class_methods import add_machine_pin_call
from stubber.publish.package import GENERIC, GENERIC_L
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

## Helper function


def get_base(candidate: Dict[str, str], version: Optional[str] = None):
    if not version:
        version = clean_version(candidate["version"], flat=True)
    base = f"{candidate['family']}-{version}"
    return base.lower()


def board_folder_name(fw: Dict, *, version: Optional[str] = None):
    """Return the name of the firmware folder. Can be in AnyCase."""
    base = get_base(fw, version=version)
    folder_name = (
        f"{base}-{fw['port']}" if fw["board"] in GENERIC else f"{base}-{fw['port']}-{fw['board']}"
    )
    # do NOT force name to lowercase
    # remove GENERIC Prefix
    folder_name = folder_name.replace("-generic_", "-").replace("-GENERIC_", "-")
    return folder_name


def get_board_path(fw: Dict):
    return CONFIG.stub_path / board_folder_name(fw)


def get_merged_path(fw: Dict):
    return CONFIG.stub_path / (board_folder_name(fw) + "-merged")


def merge_all_docstubs(
    versions: Optional[Union[List[str], str]] = None,
    family: str = "micropython",
    ports: Optional[Union[List[str], str]] = None,
    boards: Optional[Union[List[str], str]] = None,
    *,
    mpy_path: Path = CONFIG.mpy_path,
):
    """merge docstubs and board stubs to merged stubs"""
    if versions is None:
        versions = [CONFIG.stable_version]
    if ports is None:
        ports = ["auto"]
    if boards is None:
        boards = [GENERIC_L]
    if isinstance(versions, str):
        versions = [versions]
    if isinstance(ports, str):
        ports = [ports]
    if isinstance(boards, str):
        boards = [boards]

    candidates = list(board_candidates(versions=versions, family=family))
    candidates = filter_list(candidates, ports, boards)
    log.info(f"checking {len(candidates)} possible board candidates")

    merged = 0
    if not candidates:
        log.error("No candidates found")
        return
    for candidate in candidates:
        # check if we have board stubs of this version and port
        doc_path = CONFIG.stub_path / f"{get_base(candidate)}-docstubs"
        if not doc_path.exists():
            log.warning(f"No docstubs found for {candidate['version']}")
            continue
        # src and dest paths
        board_path = get_board_path(candidate)
        merged_path = get_merged_path(candidate)

        if not board_path.exists():
            log.info(f"no firmware stubs found in {board_path}")
            if candidate["version"] == "latest":
                # for the latest we do a bit more effort to get something 'good enough'
                # try to get the board_path from the last released version as the basis
                board_path = CONFIG.stub_path / board_folder_name(candidate, version="latest")
                # check again
                if board_path.exists():
                    log.info(f"using {board_path.name} as the basis for {merged_path.name}")
                else:
                    # only continue if both folders exist
                    log.debug(f"skipping {merged_path.name}, no firmware stubs found")
                    continue
            else:
                # only continue if both folders exist
                log.debug(f"skipping {merged_path.name}, no firmware stubs found")
                continue
        log.info(f"Merge docstubs for {merged_path.name} {candidate['version']}")
        result = copy_and_merge_docstubs(board_path, merged_path, doc_path)
        # Add methods from docstubs to the firmware stubs that do not exist in the firmware stubs
        # Add the __call__ method to the machine.Pin and pyb.Pin class
        add_machine_pin_call(merged_path, candidate["version"])
        if result:
            merged += 1
    log.info(f"merged {merged} of {len(candidates)} candidates")
    return merged


def copy_and_merge_docstubs(fw_path: Path, dest_path: Path, docstub_path: Path):
    """
    Parameters:
        fw_path: Path to firmware stubs (absolute path)
        dest_path: Path to destination (absolute path)
        mpy_version: micropython version ('1.18')

    Copy files from the firmware stub folders to the merged
    - 1 - Copy all firmware stubs to the package folder
    - 1.B - clean up a little bit
    - 2 - Enrich the firmware stubs with the document stubs

    """
    if dest_path.exists():
        # delete all files and folders from the destination
        shutil.rmtree(dest_path, ignore_errors=True)
    dest_path.mkdir(parents=True, exist_ok=True)

    # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
    try:
        log.trace(f"Copying firmware stubs from {fw_path}")
        shutil.copytree(fw_path, dest_path, symlinks=True, dirs_exist_ok=True)
    except OSError as e:
        log.error(f"Error copying stubs from : { fw_path}, {e}")
        raise (e)
    # rename the module.json file to firmware.json
    if (dest_path / "modules.json").exists():
        (dest_path / "modules.json").rename(dest_path / "firmware_stubs.json")

    # avoid duplicate modules : folder - file combinations
    # prefer folder from frozen stubs, over file from firmware stubs
    # No frozen here - OLD code ?
    for f in dest_path.glob("*"):
        if f.is_dir():
            for suffix in [".py", ".pyi"]:
                if (dest_path / f.name).with_suffix(suffix).exists():
                    (dest_path / f.name).with_suffix(suffix).unlink()

    # delete builtins.pyi in the package folder
    for name in [
        "builtins",  # creates conflicts, better removed
        "pycopy_imphook",  # is not intended to be used directly, and has an unresolved subclass
    ]:
        for suffix in [".py", ".pyi"]:
            if (dest_path / name).with_suffix(suffix).exists():
                (dest_path / name).with_suffix(suffix).unlink()

    # 2 - Enrich the firmware stubs with the document stubs
    result = enrich_folder(dest_path, docstub_path=docstub_path, write_back=True)

    # copy the docstubs manifest.json file to the package folder
    # if (docstub_path / "modules.json").exists():
    shutil.copy(docstub_path / "modules.json", dest_path / "doc_stubs.json")
    return result
