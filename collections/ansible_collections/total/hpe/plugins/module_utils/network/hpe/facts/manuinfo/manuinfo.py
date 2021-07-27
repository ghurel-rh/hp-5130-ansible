# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The hpe manuinfo fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.total.hpe.plugins.module_utils.network.hpe.rm_templates.manuinfo import (
    ManuinfoTemplate,
)
from ansible_collections.total.hpe.plugins.module_utils.network.hpe.argspec.manuinfo.manuinfo import (
    ManuinfoArgs,
)

class ManuinfoFacts(object):
    """ The hpe manuinfo facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = ManuinfoArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Manuinfo network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = connection.get("display current-configuration")

        # parse native config using the Manuinfo template
        manuinfo_parser = ManuinfoTemplate(lines=data.splitlines(), module=self._module)
        objs = list(manuinfo_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('manuinfo', None)

        params = utils.remove_empties(
            manuinfo_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['manuinfo'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
