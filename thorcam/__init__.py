# encoding: utf-8
# isort:skip

import os

from sdsstools import get_config, get_logger, get_package_version


NAME = "sdss-thorcam"

__version__ = get_package_version(__file__, "sdss-thorcam") or "dev"

config_file = os.path.join(os.path.dirname(__file__), "etc/thorcam.yaml")
config = get_config("thorcam", config_file=config_file)

OBSERVATORY = os.environ.get("OBSERVATORY", "UNKNOWN")

log = get_logger(NAME)
