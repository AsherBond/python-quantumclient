#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest_lib import exceptions

from neutronclient.tests.functional import base


class SimpleReadOnlyNeutronClientTest(base.ClientTestBase):

    """This is a first pass at a simple read only python-neutronclient test.
    This only exercises client commands that are read only.

    This should test commands:
    * as a regular user
    * as a admin user
    * with and without optional parameters
    * initially just check return codes, and later test command outputs

    """

    def test_admin_fake_action(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.neutron,
                          'this-does-neutron-exist')

    # NOTE(mestery): Commands in order listed in 'neutron help'

    # Optional arguments:

    def test_admin_version(self):
        self.neutron('', flags='--version')

    def test_admin_debug_list(self):
        self.neutron('net-list', flags='--debug')

    def test_admin_timeout(self):
        self.neutron('net-list', flags='--http-timeout %d' % 10)
