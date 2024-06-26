# Copyright (c) 2016 Juniper Networks Inc.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.osc import utils as nc_osc_utils
from neutronclient.osc.v2.networking_bgpvpn import constants

LOG = logging.getLogger(__name__)


class CreateBgpvpnResAssoc(command.ShowOne):
    """Create a BGP VPN resource association"""
    _action = 'create'

    def get_parser(self, prog_name):
        parser = super(CreateBgpvpnResAssoc, self).get_parser(prog_name)
        nc_osc_utils.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=(_("BGP VPN to apply the %s association (name or ID)") %
                  self._assoc_res_name),
        )
        parser.add_argument(
            'resource',
            metavar="<%s>" % self._assoc_res_name,
            help=(_("%s to associate the BGP VPN (name or ID)") %
                  self._assoc_res_name.capitalize()),
        )

        get_common_parser = getattr(self, '_get_common_parser', None)
        if callable(get_common_parser):
            get_common_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn)
        find_res_method = getattr(
            client, 'find_%s' % self._assoc_res_name)
        assoc_res = find_res_method(parsed_args.resource)
        body = {'%s_id' % self._assoc_res_name: assoc_res['id']}
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = nc_osc_utils.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            body['tenant_id'] = project_id

        arg2body = getattr(self, '_args2body', None)
        if callable(arg2body):
            body.update(
                arg2body(bgpvpn['id'], parsed_args))

        if self._resource == constants.NETWORK_ASSOC:
            obj = client.create_bgpvpn_network_association(
                bgpvpn['id'], **body)
        elif self._resource == constants.PORT_ASSOC:
            obj = client.create_bgpvpn_port_association(bgpvpn['id'], **body)
        else:
            obj = client.create_bgpvpn_router_association(
                bgpvpn['id'], **body)
        transform = getattr(self, '_transform_resource', None)
        if callable(transform):
            transform(obj)
        display_columns, columns = nc_osc_utils._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns,
                                             formatters=self._formatters)
        return display_columns, data


class SetBgpvpnResAssoc(command.Command):
    """Set BGP VPN resource association properties"""
    _action = 'set'

    def get_parser(self, prog_name):
        parser = super(SetBgpvpnResAssoc, self).get_parser(prog_name)
        parser.add_argument(
            'resource_association_id',
            metavar="<%s association ID>" % self._assoc_res_name,
            help=(_("%s association ID to update") %
                  self._assoc_res_name.capitalize()),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=(_("BGP VPN the %s association belongs to (name or ID)") %
                  self._assoc_res_name),
        )

        get_common_parser = getattr(self, '_get_common_parser', None)
        if callable(get_common_parser):
            get_common_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn)
        arg2body = getattr(self, '_args2body', None)
        if callable(arg2body):
            body = arg2body(bgpvpn['id'], parsed_args)
            if self._resource == constants.NETWORK_ASSOC:
                client.update_bgpvpn_network_association(
                    bgpvpn['id'], parsed_args.resource_association_id, **body)
            elif self._resource == constants.PORT_ASSOC:
                client.update_bgpvpn_port_association(
                    bgpvpn['id'], parsed_args.resource_association_id, **body)
            else:
                client.update_bgpvpn_router_association(
                    bgpvpn['id'], parsed_args.resource_association_id, **body)


class UnsetBgpvpnResAssoc(SetBgpvpnResAssoc):
    """Unset BGP VPN resource association properties"""
    _action = 'unset'


class DeleteBgpvpnResAssoc(command.Command):
    """Remove a BGP VPN resource association(s) for a given BGP VPN"""

    def get_parser(self, prog_name):
        parser = super(DeleteBgpvpnResAssoc, self).get_parser(prog_name)
        parser.add_argument(
            'resource_association_ids',
            metavar="<%s association ID>" % self._assoc_res_name,
            nargs="+",
            help=(_("%s association ID(s) to remove") %
                  self._assoc_res_name.capitalize()),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=(_("BGP VPN the %s association belongs to (name or ID)") %
                  self._assoc_res_name),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn)
        fails = 0
        for id in parsed_args.resource_association_ids:
            try:
                if self._resource == constants.NETWORK_ASSOC:
                    client.delete_bgpvpn_network_association(bgpvpn['id'], id)
                elif self._resource == constants.PORT_ASSOC:
                    client.delete_bgpvpn_port_association(bgpvpn['id'], id)
                else:
                    client.delete_bgpvpn_router_association(bgpvpn['id'], id)
                LOG.warning(
                    "%(assoc_res_name)s association %(id)s deleted",
                    {'assoc_res_name': self._assoc_res_name.capitalize(),
                     'id': id})
            except Exception as e:
                fails += 1
                LOG.error("Failed to delete %(assoc_res_name)s "
                          "association with ID '%(id)s': %(e)s",
                          {'assoc_res_name': self._assoc_res_name,
                           'id': id,
                           'e': e})
        if fails > 0:
            msg = (_("Failed to delete %(fails)s of %(total)s "
                     "%(assoc_res_name)s BGP VPN association(s).") %
                   {'fails': fails,
                    'total': len(parsed_args.resource_association_ids),
                    'assoc_res_name': self._assoc_res_name})
            raise exceptions.CommandError(msg)


class ListBgpvpnResAssoc(command.Lister):
    """List BGP VPN resource associations for a given BGP VPN"""

    def get_parser(self, prog_name):
        parser = super(ListBgpvpnResAssoc, self).get_parser(prog_name)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN listed associations belong to (name or ID)"),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output"),
        )
        parser.add_argument(
            '--property',
            metavar="<key=value>",
            help=_("Filter property to apply on returned BGP VPNs (repeat to "
                   "filter on multiple properties)"),
            action=parseractions.KeyValueAction,
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn)
        params = {}
        if parsed_args.property:
            params.update(parsed_args.property)
        if self._resource == constants.NETWORK_ASSOC:
            objs = client.bgpvpn_network_associations(
                bgpvpn['id'], retrieve_all=True, **params)
        elif self._resource == constants.PORT_ASSOC:
            objs = client.bgpvpn_port_associations(
                bgpvpn['id'], retrieve_all=True, **params)
        else:
            objs = client.bgpvpn_router_associations(
                bgpvpn['id'], retrieve_all=True, **params)
        transform = getattr(self, '_transform_resource', None)
        transformed_objs = []
        if callable(transform):
            for obj in objs:
                transformed_objs.append(transform(obj))
        else:
            transformed_objs = list(objs)
        headers, columns = column_util.get_column_definitions(
            self._attr_map, long_listing=parsed_args.long)
        return (headers, (osc_utils.get_dict_properties(
            s, columns, formatters=self._formatters)
            for s in transformed_objs))


class ShowBgpvpnResAssoc(command.ShowOne):
    """Show information of a given BGP VPN resource association"""

    def get_parser(self, prog_name):
        parser = super(ShowBgpvpnResAssoc, self).get_parser(prog_name)
        parser.add_argument(
            'resource_association_id',
            metavar="<%s association ID>" % self._assoc_res_name,
            help=(_("%s association ID to look up") %
                  self._assoc_res_name.capitalize()),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the association belongs to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn)
        if self._resource == constants.NETWORK_ASSOC:
            obj = client.get_bgpvpn_network_association(
                bgpvpn['id'], parsed_args.resource_association_id)
        elif self._resource == constants.PORT_ASSOC:
            obj = client.get_bgpvpn_port_association(
                bgpvpn['id'], parsed_args.resource_association_id)
        else:
            obj = client.get_bgpvpn_router_association(
                bgpvpn['id'], parsed_args.resource_association_id)
        transform = getattr(self, '_transform_resource', None)
        if callable(transform):
            transform(obj)
        display_columns, columns = nc_osc_utils._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns,
                                             formatters=self._formatters)
        return display_columns, data
