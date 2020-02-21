# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    # Standard F5 CS documentation fragment
    DOCUMENTATION = r'''
options:
  preferred_account_id:
    description:
      - If the F5 Cloud Services user is associated with multiple accounts or have configured divisions, then
        C(preferred_account_id) is required to disambiguate the account information. Not providing the parameter in such
        instances will lead to unexpected behavior which will result in incomplete resources.
    type: str
'''
