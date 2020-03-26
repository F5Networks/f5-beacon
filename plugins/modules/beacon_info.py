#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = r'''
---
module: beacon_info
short_description: Collect information from F5 Beacon service
description:
  - CCollect information from F5 Beacon service.
version_added: "f5_beacon 1.0"
options:
  gather_subset:
    description:
      - When supplied, this argument will restrict the information returned to a given subset.
      - Can specify a list of values to include a larger subset.
      - Values can also be used with an initial C(!) to specify that a specific subset
        should not be collected.
    type: list
    required: True
    choices:
      - all
      - tokens
      - sources
      - "!all"
      - "!tokens"
      - "!sources"
    aliases: ['include']
extends_documentation_fragment: f5networks.f5_beacon.f5cs
author:
  - Wojciech Wypior (@wojtek0806)
'''

EXAMPLES = r'''
- hosts: all
  collections:
    - f5networks.f5_beacon
  connection: httpapi

  vars:
    ansible_user: "foo@fakemail.net"
    ansible_httpapi_password: "password"
    ansible_network_os: f5networks.f5_beacon.f5
    ansible_httpapi_use_ssl: yes
  
  tasks:
    - name: Collect Beacon information
      beacon_info:
        gather_subset:
          - tokens
          - sources
    
    - name: Collect all Beacon information
      beacon_info:
        gather_subset:
          - all
    
    - name: Collect all Beacon information except sources
      beacon_info:
        gather_subset:
          - all
          - "!sources"
'''

RETURN = r'''
sources:
  description: List of Beacon sources information.
  returned: When C(sources) is specified in C(gather_subset).
  type: complex
  contains:
    name:
      description:
        - Placeholder text.
      returned: queried
      type: str
      sample: bit3.lab5.defense.net
    type:
      description:
        - Placeholder text.
      returned: queried
      type: str
      sample: bigip-system
    token_name:
      description:
        - Placeholder text.
      returned: queried
      type: str
      sample: "foo_token"
    last_feed_time:
      description:
        - Placeholder text.
      returned: queried
      type: str
      sample: "2020-02-20T18:06:41Z"
  sample: hash/dictionary of values
tokens:
  description: List of Beacon tokens information.
  returned: When C(tokens) is specified in C(gather_subset).
  type: complex
  contains:
    name:
      description:
        - Name of the token generated. 
      returned: queried
      type: str
      sample: foo_token
    description:
      description:
        - User defined description of the token.
      returned: queried
      type: str
      sample: "This is a test
    access_token:
      description:
        - The value of the token that has been created.
      type: str
      returned: queried
      sample: "a-aLnq7vd1S#GlHenr1Ibe7S3cC6WtUQz5t1bdgcDDo7T6Zs5f71mAc="
    source_count:
      description:
        - Placeholder text.
      returned: queried
      type: int
      sample: 2
    create_time:
      descripton:
        - Placeholder text.
      returned: queried
      sample: "2020-02-12T13:30:44.272728Z"
  sample: hash/dictionary of values      
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.six import iteritems
from ansible.module_utils.six import string_types

try:
    from plugins.module_utils.common import AnsibleF5Parameters
    from plugins.module_utils.common import F5CollectionError
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.module_utils.common import AnsibleF5Parameters
    from ansible_collections.f5networks.f5_beacon.plugins.module_utils.common import F5CollectionError


class Parameters(AnsibleF5Parameters):
    @property
    def gather_subset(self):
        if isinstance(self._values['gather_subset'], string_types):
            self._values['gather_subset'] = [self._values['gather_subset']]
        elif not isinstance(self._values['gather_subset'], list):
            raise F5CollectionError(
                "The specified gather_subset must be a list."
            )
        tmp = list(set(self._values['gather_subset']))
        tmp.sort()
        self._values['gather_subset'] = tmp

        return self._values['gather_subset']


class BaseParameters(Parameters):
    def to_return(self):
        result = {}
        for returnable in self.returnables:
            result[returnable] = getattr(self, returnable)
        result = self._filter_params(result)
        return result


class BaseManager(object):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.get('module', None)
        self.client = kwargs.get('client', None)
        self.kwargs = kwargs
        self.preferred_account_id = self.module.params.get('preferred_account_id', None)

    def exec_module(self):
        results = []
        facts = self.read_facts()
        for item in facts:
            attrs = item.to_return()
            results.append(attrs)
        return results


class TokenParameters(BaseParameters):
    api_map = {
        'createTime': 'create_time',
        'accessToken': 'access_token',
        'sourceCount': 'source_count',
    }

    returnables = [
        'name',
        'description',
        'access_token',
        'source_count',
        'create_time'
    ]


class TokenManager(BaseManager):
    def __init__(self, *args, **kwargs):
        self.client = kwargs.get('client', None)
        self.module = kwargs.get('module', None)
        super(TokenManager, self).__init__(**kwargs)
        self.want = TokenParameters(params=self.module.params)

    def exec_module(self):
        facts = self._exec_module()
        result = dict(tokens=facts)
        return result

    def _exec_module(self):
        results = []
        facts = self.read_facts()
        for item in facts:
            attrs = item.to_return()
            results.append(attrs)
        results = sorted(results, key=lambda k: k['name'])
        return results

    def read_facts(self):
        results = []
        collection = self.read_collection_from_device()
        for resource in collection:
            params = TokenParameters(params=resource)
            results.append(params)
        return results

    def read_collection_from_device(self):
        uri = '/beacon/v1/telemetry-token'
        response = self.client.get(uri, account_id=self.preferred_account_id)
        if response['code'] != 200:
            raise F5CollectionError(response['contents'])
        if 'tokens' not in response['contents'] or len(response['contents']['tokens']) == 0:
            return []
        result = response['contents']['tokens']
        return result


class SourcesParameters(BaseParameters):
    api_map = {
        'lastFeedTime': 'last_feed_time',
        'tokenName': 'token_name'
    }

    returnables = [
        'name',
        'type',
        'last_feed_time',
        'token_name',
    ]


class SourcesManager(BaseManager):
    def __init__(self, *args, **kwargs):
        self.client = kwargs.get('client', None)
        self.module = kwargs.get('module', None)
        super(SourcesManager, self).__init__(**kwargs)
        self.want = SourcesParameters(params=self.module.params)

    def exec_module(self):
        facts = self._exec_module()
        result = dict(sources=facts)
        return result

    def _exec_module(self):
        results = []
        facts = self.read_facts()
        for item in facts:
            attrs = item.to_return()
            results.append(attrs)
        results = sorted(results, key=lambda k: k['name'])
        return results

    def read_facts(self):
        results = []
        collection = self.read_collection_from_device()
        for resource in collection:
            params = SourcesParameters(params=resource)
            results.append(params)
        return results

    def read_collection_from_device(self):
        uri = '/beacon/v1/sources'
        response = self.client.get(uri, account_id=self.preferred_account_id)
        if response['code'] != 200:
            raise F5CollectionError(response['contents'])
        if 'sources' not in response['contents'] or len(response['contents']['sources']) == 0:
            return []
        result = response['contents']['sources']
        return result


class ModuleManager(object):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.get('module', None)
        self.client = kwargs.get('client', None)
        self.kwargs = kwargs
        self.want = Parameters(params=self.module.params)
        self.managers = {
            'tokens': TokenManager,
            'sources': SourcesManager,
        }

    def exec_module(self):
        self.handle_all_keyword()
        res = self.check_valid_gather_subset(self.want.gather_subset)
        if res:
            invalid = ','.join(res)
            raise F5CollectionError(
                "The specified 'gather_subset' options are invalid: {0}".format(invalid)
            )
        result = self.filter_excluded_facts()

        managers = []
        for name in result:
            manager = self.get_manager(name)
            if manager:
                managers.append(manager)

        if not managers:
            result = dict(
                queried=False
            )
            return result

        result = self.execute_managers(managers)
        if result:
            result['queried'] = True
        else:
            result['queried'] = False
        return result

    def filter_excluded_facts(self):
        # Remove the excluded entries from the list of possible facts
        exclude = [x[1:] for x in self.want.gather_subset if x[0] == '!']
        include = [x for x in self.want.gather_subset if x[0] != '!']
        result = [x for x in include if x not in exclude]
        return result

    def handle_all_keyword(self):
        if 'all' not in self.want.gather_subset:
            return
        managers = list(self.managers.keys()) + self.want.gather_subset
        managers.remove('all')
        self.want.update({'gather_subset': managers})

    def check_valid_gather_subset(self, includes):
        """Check that the specified subset is valid

        The ``gather_subset`` parameter is specified as a "raw" field which means that
        any Python type could technically be provided

        :param includes:
        :return:
        """
        keys = self.managers.keys()
        result = []
        for x in includes:
            if x not in keys:
                if x[0] == '!':
                    if x[1:] not in keys:
                        result.append(x)
                else:
                    result.append(x)
        return result

    @staticmethod
    def execute_managers(managers):
        results = dict()
        for manager in managers:
            result = manager.exec_module()
            results.update(result)
        return results

    def get_manager(self, which):
        result = {}
        manager = self.managers.get(which, None)
        if not manager:
            return result
        kwargs = dict()
        kwargs.update(self.kwargs)

        kwargs['client'] = self.client
        result = manager(**kwargs)
        return result


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = False
        argument_spec = dict(
            preferred_account_id=dict(no_log=True),
            gather_subset=dict(
                type='list',
                required=True,
                aliases=['include'],
                choices=[
                    'all',
                    'tokens',
                    'sources',
                    '!all',
                    '!tokens',
                    '!sources',
                ]
            ),
        )
        self.argument_spec = {}
        self.argument_spec.update(argument_spec)


def main():
    spec = ArgumentSpec()

    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode
    )

    try:
        mm = ModuleManager(module=module, client=Connection(module._socket_path))
        results = mm.exec_module()

        ansible_facts = dict()

        for key, value in iteritems(results):
            key = 'ansible_net_%s' % key
            ansible_facts[key] = value

        module.exit_json(ansible_facts=ansible_facts, **results)
    except F5CollectionError as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
