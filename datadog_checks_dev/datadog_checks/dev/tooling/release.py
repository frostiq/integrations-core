# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import re
from io import open

from .utils import get_version_file, load_manifest
from ..utils import read_file

# Maps the Python platform strings to the ones we have in the manifest
PLATFORMS_TO_PY = {
    'windows': 'win32',
    'mac_os': 'darwin',
    'linux': 'linux2',
}
ALL_PLATFORMS = sorted(PLATFORMS_TO_PY)

VERSION = re.compile(r'__version__ *= *(?:[\'"])(.+?)(?:[\'"])')


def get_release_tag_string(check_name, version_string):
    """
    Compose a string to use for release tags
    """
    return '{}-{}'.format(check_name, version_string)


def update_version_module(check_name, old_ver, new_ver):
    """
    Change the Python code in the __about__.py module so that `__version__`
    contains the new value.
    """
    version_file = get_version_file(check_name)
    contents = read_file(version_file)

    contents = contents.replace(old_ver, new_ver)
    with open(version_file, 'w') as f:
        f.write(contents)


def get_agent_requirement_line(check, version):
    """
    Compose a text line to be used in a requirements.txt file to install a check
    pinned to a specific version.
    """
    # base check and siblings have no manifest
    if check in ('datadog_checks_base', 'datadog_checks_tests_helper'):
        return '{}=={}'.format(check, version)

    m = load_manifest(check)
    platforms = sorted(m.get('supported_os', []))

    # all platforms
    if platforms == ALL_PLATFORMS:
        return '{}=={}'.format(check, version)
    # one specific platform
    elif len(platforms) == 1:
        return "{}=={}; sys_platform == '{}'".format(check, version, PLATFORMS_TO_PY.get(platforms[0]))
    # assuming linux+mac here for brevity
    elif platforms and 'windows' not in platforms:
        return "{}=={}; sys_platform != 'win32'".format(check, version)
    else:
        raise Exception("Can't parse the `supported_os` list for the check {}: {}".format(check, platforms))


def update_agent_requirements(req_file, check, newline):
    """
    Replace the requirements line for the given check
    """
    with open(req_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(req_file, 'w', encoding='utf-8') as f:
        for line in lines:
            check_name = line.split('==')[0]
            if check_name == check:
                f.write(newline + '\n')
            else:
                f.write(line)
