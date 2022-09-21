##########################################################################################
# config
##########################################################################################
# pragma: no cover

from loguru import logger as log
from stubber.utils.config import CONFIG

from .cli import stubber_cli


@stubber_cli.command(name="show-config")
def cli_config():
    """
    Show the current configuration
    """

    log.info(f"CONFIG.repo_path           {CONFIG.repo_path}")
    log.info(f"CONFIG.mpy_path            {CONFIG.mpy_path}")
    log.info(f"CONFIG.mpy_lib_path        {CONFIG.mpy_lib_path}")

    log.info(f"CONFIG.stub_path           {CONFIG.stub_path}")
    log.info(f"CONFIG.publish_path        {CONFIG.publish_path}")
    log.info(f"CONFIG.template_path       {CONFIG.template_path}")