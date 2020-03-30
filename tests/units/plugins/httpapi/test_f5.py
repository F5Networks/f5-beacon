# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from unittest.mock import Mock
from unittest import TestCase

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six import BytesIO, StringIO

try:
    from plugins.httpapi.f5 import HttpApi
    from plugins.httpapi.f5 import BASE_HEADERS
except ImportError:
    from ansible_collections.f5networks.f5_beacon.plugins.httpapi.f5 import HttpApi
    from ansible_collections.f5networks.f5_beacon.plugins.httpapi.f5 import BASE_HEADERS


class TestF5CloudServicesHttpApi(TestCase):
    def setUp(self):
        self.connection_mock = Mock()
        self.f5cs_plugin = HttpApi(self.connection_mock)
        self.f5cs_plugin._load_name = 'httpapi'

    def test_login_raises_exception_when_username_and_password_are_not_provided(self):
        with self.assertRaises(AnsibleConnectionFailure) as res:
            self.f5cs_plugin.login(None, None)
        assert 'Username and password are required' in str(res.exception)

    def test_login_raises_exception_when_invalid_token_response(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'BAZ': 'BAR'}
        )

        with self.assertRaises(ConnectionError) as res:
            self.f5cs_plugin.login('foo', 'bar')

        assert 'Server returned invalid response during connection authentication' in str(res.exception)

    def test_send_request_should_return_error_info_when_http_error_raises(self):
        self.connection_mock.send.side_effect = HTTPError('http://f5cs.com', 500, '', {},
                                                          StringIO('{"errorMessage": "ERROR"}'))

        resp = self.f5cs_plugin.send_request('/login', None)

        assert resp == dict(code=500, contents={'errorMessage': 'ERROR'})

    def test_login_success_properties_populated(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'access_token': 'TOKENDATA', 'refresh_token': 'REFRESHDATA', 'expires_at': '3600'}
        )

        self.f5cs_plugin.login('foo', 'bar')

        assert self.f5cs_plugin.access_token == 'TOKENDATA'
        assert self.f5cs_plugin.refresh_token == 'REFRESHDATA'
        assert self.f5cs_plugin.token_timeout == 3600
        assert self.connection_mock._auth == {'Authorization': 'Bearer TOKENDATA'}

    def test_GET_header_update_with_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        self.f5cs_plugin.get('/testlink', account_id='a-aaQsw6MlaD')
        expected_header = {'X-F5aaS-Preferred-Account-Id': 'a-aaQsw6MlaD', 'Content-Type': 'application/json'}
        self.connection_mock.send.assert_called_once_with('/testlink', None, method='GET', headers=expected_header)

    def test_GET_header_update_without_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        self.f5cs_plugin.get('/testlink')
        self.connection_mock.send.assert_called_once_with('/testlink', None, method='GET', headers=BASE_HEADERS)

    def test_POST_header_update_with_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        payload = {'Test': 'Payload'}

        self.f5cs_plugin.post('/testlink', data=payload, account_id='a-aaQsw6MlaD')
        expected_header = {'X-F5aaS-Preferred-Account-Id': 'a-aaQsw6MlaD', 'Content-Type': 'application/json'}
        self.connection_mock.send.assert_called_once_with(
            '/testlink', '{"Test": "Payload"}', headers=expected_header, method='POST'
        )

    def test_POST_header_update_without_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        payload = {'Test': 'Payload'}

        self.f5cs_plugin.post('/testlink', data=payload)
        self.connection_mock.send.assert_called_once_with(
            '/testlink', '{"Test": "Payload"}', headers=BASE_HEADERS, method='POST'
        )

    def test_PUT_header_update_with_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        payload = {'Test': 'Payload'}

        self.f5cs_plugin.put('/testlink', data=payload, account_id='a-aaQsw6MlaD')
        expected_header = {'X-F5aaS-Preferred-Account-Id': 'a-aaQsw6MlaD', 'Content-Type': 'application/json'}
        self.connection_mock.send.assert_called_once_with(
            '/testlink', '{"Test": "Payload"}', headers=expected_header, method='PUT'
        )

    def test_PUT_header_update_without_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        payload = {'Test': 'Payload'}

        self.f5cs_plugin.put('/testlink', data=payload)
        self.connection_mock.send.assert_called_once_with(
            '/testlink', '{"Test": "Payload"}', headers=BASE_HEADERS, method='PUT'
        )

    def test_PATCH_header_update_with_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        payload = {'Test': 'Payload'}

        self.f5cs_plugin.patch('/testlink', data=payload, account_id='a-aaQsw6MlaD')
        expected_header = {'X-F5aaS-Preferred-Account-Id': 'a-aaQsw6MlaD', 'Content-Type': 'application/json'}
        self.connection_mock.send.assert_called_once_with(
            '/testlink', '{"Test": "Payload"}', headers=expected_header, method='PATCH'
        )

    def test_PATCH_header_update_without_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        payload = {'Test': 'Payload'}

        self.f5cs_plugin.patch('/testlink', data=payload)
        self.connection_mock.send.assert_called_once_with(
            '/testlink', '{"Test": "Payload"}', headers=BASE_HEADERS, method='PATCH'
        )

    def test_DELTE_header_update_with_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        self.f5cs_plugin.delete('/testlink', account_id='a-aaQsw6MlaD')
        expected_header = {'X-F5aaS-Preferred-Account-Id': 'a-aaQsw6MlaD', 'Content-Type': 'application/json'}
        self.connection_mock.send.assert_called_once_with('/testlink', None, method='DELETE', headers=expected_header)

    def test_DELETE_header_update_without_account_id(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'FOO': 'BAR', 'BAZ': 'FOO'}
        )

        self.f5cs_plugin.delete('/testlink')
        self.connection_mock.send.assert_called_once_with('/testlink', None, method='DELETE', headers=BASE_HEADERS)

    @staticmethod
    def _connection_response(response, status=200):
        response_mock = Mock()
        response_mock.getcode.return_value = status
        response_text = json.dumps(response) if type(response) is dict else response
        response_data = BytesIO(response_text.encode() if response_text else ''.encode())
        return response_mock, response_data
