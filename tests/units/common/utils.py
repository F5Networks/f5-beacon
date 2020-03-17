# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import os

from unittest.mock import Mock

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.module_utils.six import BytesIO


def set_module_args(args):
    if '_ansible_remote_tmp' not in args:
        args['_ansible_remote_tmp'] = '/tmp'
    if '_ansible_keep_remote_files' not in args:
        args['_ansible_keep_remote_files'] = False

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def connection_response(name, path, status=200):
    file = os.path.join(path, name)
    with open(file, 'rb') as f:
        response_data = BytesIO(f.read())
    response_mock = Mock()
    response_mock.getcode.return_value = status
    return response_mock, response_data

