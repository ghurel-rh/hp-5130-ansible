#
# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
author: Gaëtan Hurel
cliconf: comware
short_description: Use comware cliconf to run command on HPE Comware platform
description:
- This comware plugin provides low level abstraction apis for sending and receiving CLI
  commands from HPE comware network devices (tested against HPE FlexNetwork 5130 switch serie).
version_added: 1.0.0
options:
  config_commands:
    description:
    - Specifies a list of commands that can make configuration changes
      to the target device.
    - When `ansible_network_single_user_mode` is enabled, if a command sent
      to the device is present in this list, the existing cache is invalidated.
    version_added: 2.0.0
    type: list
    default: []
    vars:
    - name: ansible_comware_config_commands
"""

import re
import time
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):
    def __init__(self, *args, **kwargs):
        self._device_info = {}
        super(Cliconf, self).__init__(*args, **kwargs)

    @enable_mode
    def get_config(self, source="current", flags=None, format=None):
        if source not in ("current", "saved"):
            raise ValueError(
                "fetching configuration from %s is not supported (use current or saved)" % source
            )

        if format:
            raise ValueError(
                "'format' value %s is not supported for get_config" % format
            )

        if not flags:
            flags = []
        if source == "current":
            cmd = "display current-configuration "
        else:
            cmd = "display saved-configuration "

        cmd += " ".join(to_list(flags))
        cmd = cmd.strip()

        return self.send_command(cmd)

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'comware'
        reply = self.get('display version')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'System image version: (\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1)

        match = re.search(r'^BOARD TYPE: (\S+)\),', data, re.M)
        if match:
            device_info['network_os_model'] = match.group(1)

        reply = self.get('display device manuinfo')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'^DEVICE_NAME[ ]+: (.+)', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    @enable_mode
    def edit_config(self, command):
        for cmd in chain(['system viewer'], to_list(command), ['end']):
            self.send_command(cmd)

    def set_cli_prompt_context(self):
        """
        Make sure we are in the operational cli mode
        :return: None
        """
        if self._connection.connected:
            self._update_cli_prompt_context(config_context=']')

    def get(
        self,
        command=None,
        prompt=None,
        answer=None,
        sendonly=False,
        output=None,
        newline=True,
        check_all=False,
    ):
        if not command:
            raise ValueError("must provide value of command to execute")
        if output:
            raise ValueError(
                "'output' value %s is not supported for get" % output
            )

        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result["rpc"] += [
            "edit_banner",
            "get_diff",
            "run_commands",
            "get_defaults_flag",
        ]
        return json.dumps(result)
