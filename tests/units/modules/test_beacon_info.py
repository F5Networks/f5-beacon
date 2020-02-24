# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from unittest.mock import Mock
from unittest import TestCase

from ansible.module_utils.basic import AnsibleModule


try:
    from plugins.httpapi.f5_cs import HttpApi
    from plugins.modules.beacon_info import TokenManager
    from plugins.modules.beacon_info import SourcesManager
    from plugins.modules.beacon_info import Parameters
    from plugins.modules.beacon_info import ModuleManager
    from plugins.modules.beacon_info import ArgumentSpec
    from tests.units.common.utils import set_module_args
    from tests.units.common.utils import connection_response
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.httpapi.f5_cs import HttpApi
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_info import TokenManager
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_info import SourcesManager
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_info import Parameters
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_info import ModuleManager
    from ansible_collections.f5networks.f5_beacon.plugins.modules.beacon_info import ArgumentSpec
    from ansible_collections.f5networks.f5_beacon.tests.units.common.utils import set_module_args
    from ansible_collections.f5networks.f5_beacon.tests.units.common.utils import connection_response


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestManager(TestCase):
    def setUp(self):
        self.spec = ArgumentSpec()
        self.connection_mock = Mock()
        self.f5cs_plugin = HttpApi(self.connection_mock)
        self.f5cs_plugin._load_name = 'httpapi'

    def test_get_beacon_tokens(self):
        set_module_args(dict(
            gather_subset=['tokens']
        ))
        self.connection_mock.send.return_value = connection_response('load_beacon_tokens.json', fixture_path)

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )
        tm = TokenManager(module=module, client=self.f5cs_plugin)
        mm = ModuleManager(module=module)
        mm.get_manager = Mock(return_value=tm)

        results = mm.exec_module()

        assert results['queried'] is True
        assert 'tokens' in results
        assert len(results['tokens']) > 0
        assert results['tokens'][0]['name'] == 'BIGIP Azure'
        assert results['tokens'][1]['source_count'] == 0
        assert results['tokens'][3]['access_token'] == 'a-aaLnQ7vd1S#SZMPaQAKOB1dGHH0P8EjajRQouqshL9VYe6EI9EoonA='

    def test_get_beacon_sources(self):
        set_module_args(dict(
            gather_subset=['sources']
        ))
        self.connection_mock.send.return_value = connection_response('load_beacon_sources.json', fixture_path)

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )
        tm = SourcesManager(module=module, client=self.f5cs_plugin)
        mm = ModuleManager(module=module)
        mm.get_manager = Mock(return_value=tm)

        results = mm.exec_module()

        assert results['queried'] is True
        assert 'sources' in results
        assert len(results['sources']) > 0
        assert results['sources'][0]['type'] == 'system'
        assert results['sources'][2]['token_name'] == 'SilverLine_BigIP_Token'
        assert results['sources'][5]['name'] == 'ip-10-0-0-105.ap-southeast-1.compute.internal'
