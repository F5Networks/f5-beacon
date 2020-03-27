# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

from unittest.mock import Mock
from unittest import TestCase

from ansible.module_utils.basic import AnsibleModule

try:
    from plugins.httpapi.f5 import HttpApi
    from plugins.modules.beacon_declaration import Parameters
    from plugins.modules.beacon_declaration import ModuleManager
    from plugins.modules.beacon_declaration import ArgumentSpec
    from tests.units.common.utils import set_module_args
    from tests.units.common.utils import connection_response
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.httpapi.f5 import HttpApi
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_declaration import Parameters
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_declaration import ModuleManager
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_declaration import ArgumentSpec
    from ansible_collections.f5networks.f5_beacon.tests.units.common.utils import set_module_args
    from ansible_collections.f5networks.f5_beacon.tests.units.common.utils import connection_response


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
            content=[
                {"foo": "bar"},
                {"baz": "foo"}
            ],
        )

        p = Parameters(params=args)
        assert {"foo": "bar"} in p.content
        assert {"baz": "foo"} in p.content


class TestManager(TestCase):
    def setUp(self):
        self.spec = ArgumentSpec()
        self.connection_mock = Mock()
        self.f5cs_plugin = HttpApi(self.connection_mock)
        self.f5cs_plugin._load_name = 'httpapi'

    def test_deploy_declaration(self, *args):
        declaration = load_fixture('test_declaration.json')
        set_module_args(dict(
            content=declaration,
            state='present'
        ))

        self.connection_mock.send.side_effect = [
            connection_response('load_declare_response.json', fixture_path),
            connection_response('load_task_status.json', fixture_path),
            connection_response('load_task_status.json', fixture_path)
        ]

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
        )

        # Override methods in the specific type of manager
        mm = ModuleManager(module=module, client=self.f5cs_plugin)

        results = mm.exec_module()
        assert results['changed'] is True
        assert results['content'] == declaration
