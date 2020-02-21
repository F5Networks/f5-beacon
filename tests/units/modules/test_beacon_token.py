# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

from unittest.mock import Mock, patch
from unittest import TestCase

from ansible.module_utils.basic import AnsibleModule

try:
    from plugins.modules.beacon_token import Parameters
    from plugins.modules.beacon_token import ModuleManager
    from plugins.modules.beacon_token import ArgumentSpec
    from tests.units.common.utils import set_module_args
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_token import Parameters
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_token import ModuleManager
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_token import ArgumentSpec
    from ansible_collections.f5networks.f5_beacon.tests.units.common.utils import set_module_args


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(TestCase):
    def test_module_parameters(self):
        args = dict(
            name='foo',
            description='token by ansible'
        )

        p = Parameters(params=args)
        assert p.name == 'foo'
        assert p.description == 'token by ansible'


class TestManager(TestCase):
    def setUp(self):
        self.spec = ArgumentSpec()

    def test_create_token_with_description(self, *args):
        set_module_args(dict(
            name='foo',
            description='token by ansible',
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
        )

        # Override methods in the specific type of manager
        mm = ModuleManager(module=module)
        mm.exists = Mock(return_value=False)
        mm.create_on_device = Mock(return_value=True)