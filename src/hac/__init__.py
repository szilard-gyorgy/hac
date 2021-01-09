import os
import click
import logging
import hac.plugins

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    level=logging.WARN,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


def main():
    click.CommandCollection(sources=hac.plugins.clickcmds)()
