#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for hpe_manuinfo
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: comware_manuinfo
short_description: 'Retrieve manufacturer info from HPE comware network device.'
description: 'Retrieve manufacturer info from HPE comware network device.'
version_added: 1.0.0
author: Gaëtan Hurel
notes:
  - 'Tested against HP FlexNetwork 5130 Switch serie'
options: {}
"""

EXAMPLES = """
- name: Retrieve manufacturer information
  comware_manuinfo:
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when state is I(merged), I(replaced), I(overridden), I(deleted) or I(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is I(merged), I(replaced), I(overridden), I(deleted) or I(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when state is I(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when state is I(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when state is I(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.total.hpe.plugins.module_utils.network.hpe.argspec.manuinfo.manuinfo import (
    ManuinfoArgs,
)
from ansible_collections.total.hpe.plugins.module_utils.network.hpe.config.manuinfo.manuinfo import (
    Manuinfo,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=ManuinfoArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Manuinfo(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
