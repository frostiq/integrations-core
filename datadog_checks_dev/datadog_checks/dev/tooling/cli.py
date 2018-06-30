# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import os

import click

from .commands import ALL_COMMANDS
from .commands.utils import CONTEXT_SETTINGS, echo_warning
from .config import config_file_exists, load_config
from .constants import set_root
from ..utils import dir_exists


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('--extras', '-e', is_flag=True, help='Work on `integrations-extras`.')
@click.option('--here', '-x', is_flag=True, help='Work on the current location.')
@click.option('--quiet', '-q', is_flag=True)
@click.version_option()
@click.pass_context
def ddev(ctx, extras, here, quiet):
    if not quiet and not config_file_exists():
        echo_warning(
            'No config file found; using default settings. Please see `ddev config -h`.'
        )

    repo_choice = 'extras' if extras else 'core'

    # Load and store configuration for sub-commands.
    config = load_config()
    config['repo_choice'] = repo_choice
    ctx.obj = config

    root = config.get(repo_choice, '')
    if here or not dir_exists(root):
        if not here and not quiet:
            echo_warning(
                '`integrations-{}` directory `{}` does not exist, defaulting '
                'to the current location.'.format(repo_choice, root)
            )
        root = os.getcwd()

    set_root(root)

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


for command in ALL_COMMANDS:
    ddev.add_command(command)
