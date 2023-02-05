"""Create a stub-only package for a specific version of micropython"""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore
import tomli_w
from loguru import logger as log
from packaging.version import Version, parse
from stubber.publish.bump import bump_postrelease
from stubber.publish.enums import StubSource
from stubber.publish.package import StubSource
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version
from stubber.publish.pypi import Version, get_pypi_versions
from pysondb import PysonDB

# TODO: Get git tag and store in DB for reference
# import stubber.basicgit as git
# git log -n 1 --format="%H"
# git log -n 1 --format="https://github.com/josverl/micropython-stubs/tree/%H"
# https://github.com/Josverl/micropython-stubs/tree/d45c8fa3dbdc01978af58532ff4c5313090aabfb

#  git -C .\all-stubs\ log -n 1 --format="https://github.com/josverl/micropython-stubs/tree/%H"

from typing import NewType

Status = NewType("Status", Dict[str, Union[str, None]])


class StubPackage:
    """
    Create a stub-only package for a specific version , port and board of micropython

    properties:
        - toml_path - the path to the `pyproject.toml` file
        - package_path - the path to the folder where the package info will be stored ('./publish').
        - pkg_version - the version of the package as used on PyPi (semver). Is stored directly in the `pyproject.toml` file
        - pyproject - the contents of the `pyproject.toml` file
    methods:
        - from_json - load the package from json
        - to_json - return the package as json

        - create_update_pyproject_toml - create or update the `pyproject.toml` file
        - create_readme - create the readme file
        - create_license - create the license file
        - copy_stubs - copy the stubs to the package folder
        - update_included_stubs - update the included stubs in the `pyproject.toml` file
        - create_hash - create a hash of the package files

        - update_package_files - combines clean, copy, and create reeadme & updates
    """

    def __init__(
        self,
        package_name: str,
        version: str = "0.0.1",
        description: str = "MicroPython stubs",
        stubs: Optional[List[Tuple[str, Path]]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a stub-only package for a specific version of micropython
        parameters:

            - package_name - the name of the package as used on PyPi
            - version - the version of the package as used on PyPi (semver)
            - description
            - stubs - a list of tuples (name, path) of the stubs to copy
            - json_data - Optional:  a json databse record that will be used to create the package from.
              When `json_data` is provided, the version, description and stubs parameters are ignored

        paths:
            ROOT_PATH - the root path of the project ('./')
            PUBLISH_PATH - root-relative path to the folder where the package info will be stored ('./publish').
            TEMPLATE_PATH - root-relative path to the folder where the template files are stored ('./publish/template').
            STUB_PATH - root-relative path to the folder where the stubs are stored ('./stubs').

        """
        if json_data is not None:

            self.from_dict(json_data)

        else:
            # store essentials
            # self.package_path = package_path
            self.package_name = package_name
            self.description = description
            self.mpy_version = clean_version(version, drop_v=True)  # Initial version
            self.hash = None  # intial hash
            """Hash of all the files in the package"""
            self.stub_hash = None  # intial hash
            """hash of the the stub files"""
            self.create_update_pyproject_toml()

            # save the stub sources
            if stubs:
                self.stub_sources = stubs
            else:
                self.stub_sources: List[Tuple[str, Path]] = []
            self._publish = True
        self.status: Status = Status({"result": "-", "name": self.package_name, "version": self.pkg_version, "error": None})

    @property
    def package_path(self) -> Path:
        "package path based on the package name and version and relative to the publish folder"
        parts = self.package_name.split("-")
        parts[1:1] = [clean_version(self.mpy_version, flat=True)]
        return CONFIG.publish_path / "-".join(parts)

    @property
    def toml_path(self) -> Path:
        "the path to the `pyproject.toml` file"
        # todo: make sure this is always relative to the root path
        return self.package_path / "pyproject.toml"

    # -----------------------------------------------
    @property
    def pkg_version(self) -> str:
        "return the version of the package"
        # read the version from the toml file
        _toml = self.toml_path
        if not _toml.exists():
            return self.mpy_version
        with open(_toml, "rb") as f:
            pyproject = tomllib.load(f)
        return str(parse(pyproject["tool"]["poetry"]["version"]))

    @pkg_version.setter
    def pkg_version(self, version: str) -> None:
        # sourcery skip: remove-unnecessary-cast
        "set the version of the package"
        if not isinstance(version, str):  # type: ignore
            version = str(version)
        # read the current file
        _toml = self.toml_path
        with open(_toml, "rb") as f:
            pyproject = tomllib.load(f)
        pyproject["tool"]["poetry"]["version"] = version

        # update the version in the toml file
        with open(_toml, "wb") as output:
            tomli_w.dump(pyproject, output)

    def update_pkg_version(self, production: bool) -> str:
        """Get the next version for the package"""
        return (
            self.get_prerelease_package_version(production) if self.mpy_version == "latest" else self.get_next_package_version(production)
        )

    def get_prerelease_package_version(self, production: bool = False) -> str:
        """Get the next prerelease version for the package."""
        base = Version("1.20")  # TODO hardcoded version - should be the next minor version after the last release
        rc = 744  # FIXME: #307 hardcoded prerelease version - should be based on the git commit count
        return str(bump_postrelease(base, rc=rc))

    def get_next_package_version(self, prod: bool = False) -> str:
        """Get the next version for the package."""
        base = Version(self.pkg_version)
        if pypi_versions := get_pypi_versions(self.package_name, production=prod, base=base):
            self.pkg_version = str(pypi_versions[-1])
        return self.bump()

    # -----------------------------------------------
    @property
    def pyproject(self) -> Union[Dict[str, Any], None]:
        "parsed pyproject.toml or None"
        pyproject = None
        _toml = self.toml_path
        if (_toml).exists():
            with open(_toml, "rb") as f:
                pyproject = tomllib.load(f)
        return pyproject

    @pyproject.setter
    def pyproject(self, pyproject: Dict) -> None:
        # check if the result is a valid toml file

        try:
            tomllib.loads(tomli_w.dumps(pyproject))
        except tomllib.TOMLDecodeError as e:
            print("Could not create a valid TOML file")
            raise (e)
        # make sure parent folder exists
        _toml = self.toml_path
        (_toml).parent.mkdir(parents=True, exist_ok=True)
        with open(_toml, "wb") as output:
            tomli_w.dump(pyproject, output)

    # -----------------------------------------------

    def to_dict(self) -> dict:
        """return the package as a dict to store in the jsondb

        need to simplify some of the Objects to allow serialisation to json
        - the paths to posix paths
        - the version (semver) to a string
        - toml file to list of lines

        """
        return {
            "name": self.package_name,
            "mpy_version": self.mpy_version,
            "publish": self._publish,
            "pkg_version": str(self.pkg_version),
            "path": self.package_path.name,  # only store the folder name , as it is relative to the publish folder
            "stub_sources": [(name, Path(path).as_posix()) for (name, path) in self.stub_sources],
            "description": self.description,
            "hash": self.hash,
            "stub_hash": self.stub_hash,
        }

    def from_dict(self, json_data: Dict) -> None:
        """load the package from a dict (from the jsondb)"""
        self.package_name = json_data["name"]
        # self.package_path = Path(json_data["path"])
        self.description = json_data["description"]
        self.mpy_version = json_data["mpy_version"]
        self._publish = json_data["publish"]
        self.hash = json_data["hash"]
        self.stub_hash = json_data["stub_hash"]
        # create folder
        if not self.package_path.exists():
            self.package_path.mkdir(parents=True, exist_ok=True)
        #  create the pyproject.toml file
        self.create_update_pyproject_toml()
        # set pkg version after creating the toml file
        self.pkg_version = json_data["pkg_version"]
        self.stub_sources = []
        for (name, path) in json_data["stub_sources"]:
            if path.startswith("stubs/"):
                path = path.replace("stubs/", "")
            self.stub_sources.append((name, Path(path)))

    def update_package_files(self) -> None:
        """
        Update the stub-only package for a specific version of micropython
         - cleans the package folder
         - copies the stubs from the list of stubs.
         - creates/updates the readme and the license file
        """
        # create the package folder
        self.package_path.mkdir(parents=True, exist_ok=True)

        self.clean()  # Delete any previous *.py? files
        self.copy_stubs()
        self.create_readme()
        self.create_license()

    def copy_stubs(self) -> None:
        """
        Copy files from all listed stub folders to the package folder
        the order of the stub folders is relevant as "last copy wins"

         - 1 - Copy all firmware stubs/merged to the package folder
         - 2 - copy the remaining stubs to the package folder
         - 3 - remove *.py files from the package folder
        """
        # First check if all stub source folders exist
        for n in range(len(self.stub_sources)):
            stub_type, fw_path = self.stub_sources[n]
            # update to use -merged
            if stub_type == StubSource.FIRMWARE:
                # Check if -merged folder exists and use that instead
                if fw_path.name.endswith("-merged"):
                    merged_path = fw_path
                else:
                    merged_path = fw_path.with_name(f"{fw_path.name}-merged")
                if (CONFIG.stub_path / merged_path).exists():
                    stub_type = StubSource.MERGED
                    # Update the source list
                    self.stub_sources[n] = (stub_type, merged_path)
                fw_path = merged_path
            # check if path exists
            if not (CONFIG.stub_path / fw_path).exists() and stub_type != StubSource.FROZEN:
                raise FileNotFoundError(f"Could not find stub source folder {fw_path}")

        # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
        # for stub_type, fw_path in [s for s in self.stub_sources]:
        for n in range(len(self.stub_sources)):
            stub_type, fw_path = self.stub_sources[n]

            try:
                log.trace(f"Copying {stub_type} from {fw_path}")
                shutil.copytree(
                    CONFIG.stub_path / fw_path,
                    self.package_path,
                    symlinks=True,
                    dirs_exist_ok=True,
                )
            except OSError as e:
                if stub_type != StubSource.FROZEN:
                    raise FileNotFoundError(f"Could not find stub source folder {fw_path}") from e
                else:
                    log.debug(f"Error copying stubs from : {CONFIG.stub_path / fw_path}, {e}")

        # 3 - clean up a little bit
        # delete all the .py files in the package folder if there is a corresponding .pyi file
        for f in self.package_path.rglob("*.py"):
            if f.with_suffix(".pyi").exists():
                f.unlink()

    def create_readme(self) -> None:
        """
        Create a readme file for the package
         - based on the template readme file
         - with a list of all included stub folders added to it (not the individual stub-files)
        """
        # read the readme file and update the version and description
        with open(CONFIG.template_path / "README.md", "r") as f:
            TEMPLATE_README = f.read()

        # add a readme with the names of the stub-folders

        # read informations from firmware_stubs.json
        firmware_stubs = {}
        doc_stubs = {}
        core_stubs = {}
        try:
            with open(self.package_path / "firmware_stubs.json", "r") as f:
                firmware_stubs = json.load(f)
            with open(self.package_path / "doc_stubs.json", "r") as f:
                doc_stubs = json.load(f)
            with open(self.package_path / "modules.json", "r") as f:
                core_stubs = json.load(f)
        except FileNotFoundError:
            pass

        # Prettify this by merging with template text
        with open(self.package_path / "README.md", "w") as f:
            f.write(f"# {self.package_name}\n\n")
            f.write(TEMPLATE_README)
            f.write(f"Included stubs:\n")
            for name, folder in self.stub_sources:
                f.write(f"* {name} from `stubs/{Path(folder).as_posix()}`\n")

            f.write(f"\n\n")
            f.write(f"origin | Family | Port | Board | Version\n")
            f.write(f"-------|--------|------|-------|--------\n")
            try:
                f.write(
                    f"Firmware | {firmware_stubs['firmware']['family']} | {firmware_stubs['firmware']['port']} | {firmware_stubs['firmware']['machine']} | {clean_version(firmware_stubs['firmware']['version'])} \n"
                )
            except Exception:
                pass
            try:
                f.write(
                    f"Documentation | {doc_stubs['firmware']['family']} | {doc_stubs['firmware']['port']} | - | {clean_version(doc_stubs['firmware']['version'])} \n"
                )
            except Exception:
                pass
            try:
                f.write(
                    f"Core | {core_stubs['firmware']['family']} | {core_stubs['firmware']['port']} | - | {clean_version(core_stubs['firmware']['version'])} \n"
                )
            except Exception:
                pass

    def create_license(self) -> None:
        """
        Create a license file for the package
         - copied from the template license file
        """
        # copy the license file from the template to the package folder
        # option : append other license files
        shutil.copy(CONFIG.template_path / "LICENSE.md", self.package_path)

    def create_update_pyproject_toml(self) -> None:
        """
        create or update/overwrite a `pyproject.toml` file by combining a template file
        with the given parameters.
        and updating it with the pyi files included
        """
        if (self.toml_path).exists():
            # do not overwrite the version of a pre-existing file
            _pyproject = self.pyproject
            assert _pyproject is not None
            # clear out the packages section
            _pyproject["tool"]["poetry"]["packages"] = []
            # update the dependencies section by readin that from the template file
            with open(CONFIG.template_path / "pyproject.toml", "rb") as f:
                tpl = tomllib.load(f)

            _pyproject["tool"]["poetry"]["dependencies"] = tpl["tool"]["poetry"]["dependencies"]

        else:
            # read the template pyproject.toml file from the template folder
            try:
                with open(CONFIG.template_path / "pyproject.toml", "rb") as f:
                    _pyproject = tomllib.load(f)
                _pyproject["tool"]["poetry"]["version"] = self.mpy_version
            except FileNotFoundError as e:
                log.error(f"Could not find template pyproject.toml file {e}")
                raise (e)

        # update the name , version and description of the package
        _pyproject["tool"]["poetry"]["name"] = self.package_name
        _pyproject["tool"]["poetry"]["description"] = self.description
        # write out the pyproject.toml file
        self.pyproject = _pyproject

    def update_included_stubs(self) -> int:
        "Add the stub files to the pyproject.toml file"
        _pyproject = self.pyproject
        assert _pyproject is not None, "No pyproject.toml file found"
        _pyproject["tool"]["poetry"]["packages"] = [
            {"include": p.relative_to(self.package_path).as_posix()} for p in sorted((self.package_path).rglob("*.pyi"))
        ]
        # write out the pyproject.toml file
        self.pyproject = _pyproject
        return len(_pyproject["tool"]["poetry"]["packages"])
        # OK

    def clean(self) -> None:
        """
        Remove the stub files from the package folder

        This is used before update the stub package, to avoid lingering stub files,
        and after the package has been built, to avoid needing to store files multiple times.

        `.gitignore` cannot be used as this will prevent poetry from processing the files.

        """
        # remove all *.py and *.pyi files in the folder
        for wc in ["*.py", "*.pyi", "modules.json"]:
            for f in (self.package_path).rglob(wc):
                f.unlink()

    def calculate_hash(self, include_md: bool = True) -> str:
        # sourcery skip: reintroduce-else, swap-if-else-branches, use-named-expression
        """
        Create a SHA1 hash of all files in the package, excluding the pyproject.toml file itself.
        the hash is based on the content of the .py/.pyi and .md files in the package.
        if include_md is False , the .md files are not hased, allowing the files in the packeges to be compared simply
        As a single has is created across all files, the files are sorted prior to hashing to ensure that the hash is stable.

        A changed hash will not indicate which of the files in the package have been changed.
        """
        # BUF_SIZE is totally arbitrary,
        BUF_SIZE = 65536 * 16  # lets read stuff in 16 x 64kb chunks!

        file_hash = hashlib.sha1()
        # Stubs Only
        files = list((self.package_path).rglob("**/*.pyi"))
        if include_md:
            files += (
                [self.package_path / "LICENSE.md"]
                + [self.package_path / "README.md"]
                # do not include [self.toml_file]
            )
        # print(f"Creating hash for {self.package_name} with {len(files)} files : ", end="" )
        for file in sorted(files):
            try:
                with open(file, "rb") as f:
                    while True:
                        data = f.read(BUF_SIZE)
                        if not data:
                            break
                        file_hash.update(data)
            except FileNotFoundError:
                log.warning(f"File not found {file}")
                # ignore file not found errors
                # this is to allow the hash to be created WHILE GIT / VIRUS SCANNERS HOLD LINGERING FILES
                pass
        # print(f"Hash: {file_hash.hexdigest()}")
        return file_hash.hexdigest()

    def update_hashes(self, ret=False) -> None:
        """Update the package hashes. Resets is_changed() to False"""
        self.hash = self.calculate_hash()
        self.stub_hash = self.calculate_hash(include_md=False)

    def is_changed(self, include_md: bool = True) -> bool:
        """Check if the package has changed, based on the current and the stored hash.
        The default checks the hash of all files, including the .md files.
        """
        current = self.calculate_hash(include_md=include_md)
        if include_md:
            stored = self.hash
        else:
            stored = self.stub_hash
        log.warning(f"changed: {self.hash != current} : Stored {stored} Current: {current}")
        return stored != current

    def bump(self, *, rc: int = 0) -> str:
        """
        bump the postrelease version of the package, and write the change to disk
        if rc > 1, the version is bumped to the specified release candidate
        """
        try:
            current = Version(self.pkg_version)
            assert isinstance(current, Version)
            # bump the version
            self.pkg_version = str(bump_postrelease(current=current, rc=rc))
        except Exception as e:  # pragma: no cover
            log.error(f"Error: {e}")
        return self.pkg_version

    def run_poetry(self, parameters: List[str]) -> bool:
        """Run a poetry commandline in the package folder.
        Note: this may write some output to the console ('All set!')
        """
        # check for pyproject.toml in folder
        if not (self.package_path / "pyproject.toml").exists():  # pragma: no cover
            log.error(f"No pyproject.toml file found in {self.package_path}")
            return False
        # todo: call poetry directly to improve error handling
        try:
            log.debug(f"poetry {parameters} starting")
            subprocess.run(
                ["poetry"] + parameters,
                cwd=self.package_path,
                check=True,
                # stdout=subprocess.PIPE,
                stdout=subprocess.PIPE,  # interestingly: errors on stdout , output on stderr .....
                universal_newlines=True,
            )
            log.trace(f"poetry {parameters} completed")
        except (NotADirectoryError, FileNotFoundError) as e:  # pragma: no cover
            log.error("Exception on process, {}".format(e))
            return False
        except subprocess.CalledProcessError as e:  # pragma: no cover
            # Detect and log  error detection om upload
            #   UploadError
            #   HTTP Error 400: File already exists. See https://test.pypi.org/help/#file-name-reuse for more information.
            # TODO: how to return the state so it can be handled
            print()  # linefeed after output
            errors = [l for l in e.stdout.splitlines()[1:7] if "Error" in l]
            for e in errors:
                log.error(e)

            # log.error("Exception on process, {}".format(e))
            return False
        return True

    def write_package_json(self) -> None:
        """write the package.json file to disk"""
        # make sure folder exists
        if not self.package_path.exists():
            self.package_path.mkdir(parents=True, exist_ok=True)
        # write the json to a file
        with open(self.package_path / "package.json", "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def check(self) -> bool:
        """check if the package is valid by running `poetry check`
        Note: this will write some output to the console ('All set!')
        """
        return self.run_poetry(["check", "-vvv"])

    def poetry_build(self) -> bool:
        """build the package by running `poetry build`"""
        return self.run_poetry(["build", "-vvv"])

    def poetry_publish(self, production: bool = False) -> bool:
        if not self._publish:
            log.warning(f"Publishing is disabled for {self.package_name}")
            return False
        # update the package info
        self.write_package_json()
        if production:
            log.debug("Publishing to PRODUCTION https://pypy.org")
            params = ["publish"]
        else:
            log.debug("Publishing to TEST-PyPi https://test.pypy.org")
            params = ["publish", "-r", "test-pypi"]
        log.error(f"Publishing {self.package_name} to {params} is Skipped")
        r = self.run_poetry(params)
        print("")  # add a newline after the output
        return r

    def are_package_sources_available(self) -> bool:
        """
        Check if (all) the packages sources exist.
        """
        ok = True
        for (name, path) in self.stub_sources:
            if not (CONFIG.stub_path / path).exists():
                # todo: below is a workaround for different types, but where is the source of this difference coming from?
                msg = (
                    f"{self.package_name}: source '{name._value_}' not found: {CONFIG.stub_path / path}"
                    if isinstance(name, StubSource)
                    else f"{self.package_name}: source '{name}' not found: {CONFIG.stub_path / path}"
                )
                if name != StubSource.FROZEN:
                    log.debug(msg)
                    self.status["error"] = msg
                    ok = False
                else:
                    # not a blocking issue if there are no frozen stubs, perhaps this port/board does not have any
                    log.debug(msg)
        return ok

    def update_package(self) -> bool:
        """Update the package files, if all the sources are available"""
        log.info(f"- Update {self.package_path.name}")
        log.trace(f"{self.package_path.as_posix()}")

        # check if the sources exist
        ok = self.are_package_sources_available()
        if not ok:
            log.debug(f"{self.package_name}: skipping as one or more source stub folders are missing")
            self.status["error"] = "Skipped, stub folder(s) missing"
            shutil.rmtree(self.package_path.as_posix())
            self._publish = False  # type: ignore
            return True
        try:
            self.update_package_files()
            self.update_included_stubs()
            self.check()
        except Exception as e:  # pragma: no cover
            log.error(f"{self.package_name}: {e}")
            self.status["error"] = str(e)
            return False
        return True

    def build(
        self,
        production: bool,  # PyPI or Test-PyPi - USED TO FIND THE NEXT VERSION NUMBER
        force=False,  # BUILD even if no changes
    ) -> bool:  # sourcery skip: default-mutable-arg, require-parameter-annotation
        """
        Build a package
        look up the previous package version in the dabase
            - update package files
            - build the wheels and sdist
        """
        log.debug("=" * 40)
        log.info(f"Build: {self.package_path.name}")
        ok = self.update_package()
        self.status["version"] = self.pkg_version
        if not ok:
            log.warning(f"{self.package_name}: skipping as build failed")
            self.status["error"] = "Build failed"
            return False
        # If there are changes to the package, then publish it
        if self.is_changed() or force:
            #  Build the distribution files
            log.info(f"Found changes to package sources: {self.package_name} {self.pkg_version} ")
            log.debug(f"Old hash {self.hash} != New hash {self.calculate_hash()}")
            old_ver = self.pkg_version
            self.status["version"] = self.update_pkg_version(production)
            # to get the next version
            log.debug(f"{self.package_name}: bump version for {old_ver} to {self.pkg_version } {production}")
            self.write_package_json()
            log.trace(f"New hash: {self.package_name} {self.pkg_version} {self.hash}")
            build_ok = self.poetry_build()
            if build_ok:
                self.status["result"] = "Build OK"
            else:
                log.warning(f"{self.package_name}: skipping as build failed")
                self.status["error"] = "Build failed"
                return False
        return True

    def publish(
        self,
        db: PysonDB,
        *,
        production: bool,  # PyPI or Test-PyPi
        build=False,  #
        force=False,  # publish even if no changes
        clean: bool = False,  # clean up afterwards
    ) -> bool:  # sourcery skip: default-mutable-arg, require-parameter-annotation
        """
        Publish a package to PyPi
        look up the previous package version in the dabase, and only publish if there are changes to the package
        - change determied by hash across all files

        Build
            - update package files
            - build the wheels and sdist
        Publish
            - publish to PyPi
            - update database with new hash
        """
        log.info(f"Publish: {self.package_path.name}")
        if self.is_changed() or build or force:
            self.build(production=production, force=True)

        self.update_pkg_version(production=production)
        # Publish the package to PyPi, Test-PyPi or Github
        if self.is_changed() or force:
            if self.mpy_version == "latest":
                log.warning("version: `latest` package will only be available on Github, and not published to PyPi.")
                self.status["result"] = "Published to GitHub"
            else:
                self.update_hashes()  # resets is_changed to False
                pub_ok = self.poetry_publish(production=production)
                if not pub_ok:
                    log.warning(f"{self.package_name}: Publish failed for {self.pkg_version}")
                    self.status["error"] = "Publish failed"                    
                    return False
                self.status["result"] = "Published to PyPi" if production else "Published to Test-PyPi"
                self.update_hashes()
                # get the package state and add it to the database
                db.add(self.to_dict())
                db.commit()
                return True
        else:
            log.debug(f"No changes to package : {self.package_name} {self.pkg_version}")

        if clean:
            self.clean()
        return True
