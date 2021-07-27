#
# (c) 2016 Red Hat Inc.
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

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text, to_bytes
from ansible.plugins.terminal import TerminalBase
from ansible.utils.display import Display

display = Display()


class TerminalModule(TerminalBase):

    terminal_stdout_re = [
        re.compile(br"[\r\n]?[\w]*\(.+\)\s*[\^\*]?(?:\[.+\])? ?#(?:\s*)$"),
        re.compile(br"[pP]assword:$"),
        re.compile(br"(?<=\s)[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\s*#\s*$"),
        re.compile(br"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?$"),
    ]

    terminal_stderr_re = [
        re.compile(br"% ?Error"),
        re.compile(br"% Unrecognized command found at ?[\s]+", re.I),
        re.compile(br"% Too many parameters found at ?[\s]+", re.I),
        re.compile(br"% Incomplete command found at ?[\s]+", re.I),
        re.compile(br"% ?Error"),
        re.compile(br"Error:", re.M),
        re.compile(br"^% \w+", re.M),
        re.compile(br"% ?Bad secret"),
        re.compile(br"invalid input", re.I),
        re.compile(br"(?:incomplete|ambiguous) command", re.I),
        re.compile(br"connection timed out", re.I),
        re.compile(br"[^\r\n]+ not found", re.I),
        re.compile(br"'[^']' +returned error code: ?\d+"),        
    ]

    terminal_config_prompt = re.compile(r"^\[.+\]$")

    def on_open_shell(self):
        try:
            #self._exec_cli_command(b"terminal width 0")
            self._exec_cli_command(b"screen-length disable")
        except AnsibleConnectionFailure:
            display.display(
                "WARNING: Unable to disable screen-length, command responses may be truncated"
            )

    def on_become(self, passwd=None):
        if self._get_prompt().startswith(b"[") and self._get_prompt().endswith(b"]"):
            return

        cmd = {u"command": u"system-view"}
        try:
            self._exec_cli_command(
                to_bytes(json.dumps(cmd), errors="surrogate_or_strict")
            )
            prompt = self._get_prompt()
            if prompt is None or not (prompt.startswith(b"[") and prompt.endswith(b"]")):
                raise AnsibleConnectionFailure(
                    "failed to elevate privilege to enable mode still at prompt [%s]"
                    % prompt
                )
        except AnsibleConnectionFailure as e:
            prompt = self._get_prompt()
            raise AnsibleConnectionFailure(
                "unable to elevate privilege to enable mode, at prompt [%s] with error: %s"
                % (prompt, e.message)
            )

    def on_unbecome(self):
        prompt = self._get_prompt()
        if prompt is None:
            # if prompt is None most likely the terminal is hung up at a prompt
            return

        if prompt.startswith(b"[") and prompt.endswith(b"]"):
            self._exec_cli_command(b"end")
