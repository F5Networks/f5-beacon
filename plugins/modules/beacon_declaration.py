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
module: Manage Beacon declarations on F5 Cloud Services
short_description: Manage Beacon declarations on F5 Cloud Services
description:
  - Manage Beacon declarations on F5 Cloud Services.
version_added: "f5_beacon 1.0"
options:
  content:
    description:
      - Full declaration of the service.
    type: raw
    required: True
extends_documentation_fragment: f5networks.f5_beacon.f5cs
author:
  - Wojciech Wypior (@wojtek0806)
'''

EXAMPLES = r'''
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.urls import urlparse
from ansible.module_utils.six import string_types

try:
    from plugins.module_utils.common import AnsibleF5Parameters
    from plugins.module_utils.common import F5CollectionError
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.module_utils.common import AnsibleF5Parameters
    from ansible_collections.f5networks.f5_beacon.plugins.module_utils.common import F5CollectionError

try:
    import json
except ImportError:
    import simplejson as json


class Parameters(AnsibleF5Parameters):
    api_map = {
    }

    api_attributes = [
    ]

    returnables = [
        'content'
    ]


class ModuleParameters(Parameters):
    @property
    def content(self):
        if self._values['content'] is None:
            return None
        if isinstance(self._values['content'], string_types):
            data = json.loads(self._values['content'] or 'null')
            return data
        else:
            return self._values['content']


class Changes(Parameters):
    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                change = getattr(self, returnable)
                if isinstance(change, dict) and 'declaration' not in change:
                    result.update(change)
                else:
                    result[returnable] = change
            result = self._filter_params(result)
        except Exception:
            raise
        return result


class UsableChanges(Changes):
    pass


class ReportableChanges(Changes):
    pass


class Difference(object):
    def __init__(self, want, have=None):
        self.want = want
        self.have = have

    def compare(self, param):
        try:
            result = getattr(self, param)
            return result
        except AttributeError:
            return self.__default(param)

    def __default(self, param):
        attr1 = getattr(self.want, param)
        try:
            attr2 = getattr(self.have, param)
            if attr1 != attr2:
                return attr1
        except AttributeError:
            return attr1


class ModuleManager(object):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop('module', None)
        self.client = kwargs.pop('client', None)
        self.url = '/beacon/v1/declare'
        self.want = ModuleParameters(params=self.module.params)
        self.changes = UsableChanges()

    def _announce_deprecations(self, result):
        warnings = result.pop('__warnings', [])
        for warning in warnings:
            self.module.deprecate(
                msg=warning['msg'],
                version=warning['version']
            )

    def _set_changed_options(self):
        changed = {}
        for key in Parameters.returnables:
            if getattr(self.want, key) is not None:
                changed[key] = getattr(self.want, key)
        if changed:
            self.changes = UsableChanges(params=changed)

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        if state == "present":
            changed = self.present()
        elif state == "absent":
            changed = self.absent()

        reportable = ReportableChanges(params=self.changes.to_return())
        changes = reportable.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        self._announce_deprecations(result)
        return result

    def present(self):
        return self.create()

    def absent(self):
        return self.remove()

    def remove(self):
        if self.module.check_mode:
            return True
        self.remove_from_device()
        return True

    def create(self):
        self._set_changed_options()
        if self.module.check_mode:
            return True
        self.create_on_device()
        return True

    def check_for_task(self, task):
        url = urlparse(task).path
        for x in range (0, 60):
            response = self.client.get(url, account_id=self.want.preferred_account_id)
            if response['code'] == 200:
                if response['contents']['status'] == 'Completed':
                    return True
                if response['contents']['status'] == 'Failed':
                    raise F5CollectionError(response['contents']['error'])
            else:
                raise F5CollectionError(response['code'], response['contents'])

    def create_on_device(self):
        payload = {
            "action": "deploy",
        }
        try:
            payload.update(self.want.content)
        except ValueError:
            raise F5CollectionError(
                "The provided 'declaration' could not be converted into valid json. If you "
                "are using the 'to_nice_json' filter, please remove it."
            )
        response = self.client.post(self.url, data=payload, account_id=self.want.preferred_account_id)
        if response['code'] == 200:
            task = response['contents']['taskReference']
            return self.check_for_task(task)
        else:
            raise F5CollectionError(response['code'], response['contents'])

    def remove_from_device(self):
        payload = {
            "action": "remove",
        }
        try:
            payload.update(self.want.content)
        except ValueError:
            raise F5CollectionError(
                "The provided 'declaration' could not be converted into valid json. If you "
                "are using the 'to_nice_json' filter, please remove it."
            )
        response = self.client.post(self.url, data=payload, account_id=self.want.preferred_account_id)
        if response['code'] == 200:
            task = response['contents']['taskReference']
            return self.check_for_task(task)
        else:
            raise F5CollectionError(response['code'], response['contents'])


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        argument_spec = dict(
            content=dict(type='raw', required=True),
            preferred_account_id=dict(no_log=True),
            state=dict(
                default='present',
                choices=['present', 'absent']
            ),
        )
        self.argument_spec = {}
        self.argument_spec.update(argument_spec)


def main():
    spec = ArgumentSpec()

    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode,
    )

    try:
        mm = ModuleManager(module=module, client=Connection(module._socket_path))
        results = mm.exec_module()
        module.exit_json(**results)
    except F5CollectionError as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
