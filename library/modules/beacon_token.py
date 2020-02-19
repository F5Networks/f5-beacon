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
module: Manage Beacon tokens on F5 Cloud Services
short_description: Manage Beacon tokens on F5 Cloud Services
description:
  - Manage Beacon tokens on F5 Cloud Services.
version_added: "f5_beacon 1.0"
options:
  name:
    description:
      - Specifies the name of the Beacon token to manage/create.
    type: str
    required: True
  description:
    description:
      - User created token description.
    type: str
  preferred_account_id:
    description:
      - If the F5 Cloud Services user is associated with multiple accounts or have configured divisions, then
        C(preferred_account_id) is required to disambiguate the account information. Not providing the parameter in such
        instances will lead to unexpected behavior which will result in incomplete resources.
    type: str
author:
  - Wojciech Wypior (@wojtek0806)
'''

EXAMPLES = r'''
- name: Create Beacon Token with description
  beacon_token:
    name: "foobar"
    description: "Created by Ansible tool"
    state: present

- name: Delete Beacon Token
  beacon_token:
    name: "foobar"
    state: absent
    
- name: Create Beacon Token with description, preferred account provided
  beacon_token:
    name: "foobar"
    description: "Created by Ansible tool"
    preferred_account_id: "a-aaSXXdAYYY2"
    state: present
'''

RETURN = r'''
name:
  description: The name of the created token.
  returned: changed
  type: str
  sample: Token_foo
description:
  description: The new description of the token.
  returned: changed
  type: str
  sample: "My Token"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

try:
    from library.module_utils.common import AnsibleF5Parameters
    from library.module_utils.common import F5CollectionError
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.module_utils.common import AnsibleF5Parameters
    from ansible_collections.f5networks.f5_beacon.plugins.module_utils.common import F5CollectionError


class Parameters(AnsibleF5Parameters):
    api_map = {
    }

    api_attributes = [
        'name',
        'description',
    ]

    returnables = [
        'name',
        'description',
    ]


class ModuleParameters(Parameters):
    pass


class Changes(Parameters):
    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                change = getattr(self, returnable)
                if isinstance(change, dict):
                    result.update(change)
                else:
                    result[returnable] = change
            result = self._filter_params(result)
        except Exception:
            pass
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
        self.url = '/beacon/v1/telemetry-token'
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

        return False

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
        if self.exists():
            return False
        else:
            return self.create()

    def absent(self):
        if self.exists():
            return self.remove()
        return False

    def remove(self):
        if self.module.check_mode:
            return True
        self.remove_from_device()
        if self.exists():
            raise F5CollectionError("Failed to delete the resource.")
        return True

    def create(self):
        self._set_changed_options()
        if self.module.check_mode:
            return True
        self.create_on_device()
        return True

    def exists(self):
        response = self.client.get(self.url + '/' + self.want.name, account_id=self.want.preferred_account_id)
        if response['code'] == 404:
            return False
        elif response['code'] == 200:
            return True
        else:
            raise F5CollectionError(response['contents'])

    def create_on_device(self):
        params = self.changes.api_params()
        response = self.client.post(self.url, data=params, account_id=self.want.preferred_account_id)
        if response['code'] == 200:
            return True
        else:
            raise F5CollectionError(response['code'], response['contents'])

    def remove_from_device(self):
        response = self.client.delete(self.url + '/' + self.want.name, account_id=self.want.preferred_account_id)
        if response['code'] == 200:
            return True
        else:
            raise F5CollectionError(response['code'], response['contents'])


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        argument_spec = dict(
            name=dict(required=True),
            description=dict(),
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
