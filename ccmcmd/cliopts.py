import argparse

def args(configread):
    parser = argparse.ArgumentParser(description='CCM Team command tools.', usage='%(prog)s [OPTIONS]')
    subparsers = parser.add_subparsers(title="apps", dest="apps")

    opt_consul = subparsers.add_parser('consul')
    opt_consul.add_argument("--fqdn", help="Consul Host FQDN.", required=True)
    opt_consul.add_argument("--location", help="Consul Host Datacenter Location.", required=False, default=configread['common']['location_default'])

    opt_icinga = subparsers.add_parser('icinga')
    opt_icinga.add_argument("--fqdn", help="Icinga Host FQDN.", required=True)
    opt_icinga.add_argument("--location", help="Icinga Host Datacenter Location.", required=False, default=configread['common']['location_default'])

    subparsers = opt_consul.add_subparsers(title="consul", dest="consul")

    opt_consul_keyval_get = subparsers.add_parser('keyval-get')
    opt_consul_keyval_get.add_argument( "--app", required=False,
        choices=configread['consul']['common']['kv_apps_available'],
        help="""Consul KV apps.
                Immutable apps: {}""".format(', '.join(configread['consul']['common']['kv_apps_immutable'])
        )
    )
    opt_consul_keyval_get.add_argument("--filter_re", help="RegEx filter. (case insensitive)", required=False)
    opt_consul_keyval_get.add_argument("--filter_col", help="Filter Key and Value columns.", required=False, choices=['key', 'value'])

    opt_consul_keyval_put = subparsers.add_parser('keyval-put')
    opt_consul_keyval_put.add_argument("--key", help="Consul Key Name.", required=True)
    opt_consul_keyval_put.add_argument("--value", help="Consul Key Value.", required=True)
    opt_consul_keyval_put.add_argument("--app", required=True,
        choices=list(set(configread['consul']['common']['kv_apps_available']) - set(configread['consul']['common']['kv_apps_immutable'])),
        help="""Consul KV available apps.
                Immutable apps: {}""".format(', '.join(configread['consul']['common']['kv_apps_immutable'])
        )
    )

    opt_consul_keyval_delete = subparsers.add_parser('keyval-delete')
    opt_consul_keyval_delete.add_argument("--key", help="Consul Key.", required=False, default=None)
    opt_consul_keyval_delete.add_argument("--app", required=False, default=None,
        choices=list(set(configread['consul']['common']['kv_apps_available']) - set(configread['consul']['common']['kv_apps_immutable'])),
        help="""Consul KV available apps.
                Immutable apps: {}""".format(', '.join(configread['consul']['common']['kv_apps_immutable'])
        )
    )
    opt_consul_keyval_delete.add_argument("--force", help="Force delete keys.", required=False, action='store_true')

    subparsers = opt_icinga.add_subparsers(title="icinga", dest="icinga")

    opt_icinga_downtime = subparsers.add_parser('downtime-set', help="Set Icinga downtime for max {} hours.".format(configread['icinga']['common']['downtime_max_hours']))
    opt_icinga_downtime.add_argument("--hours", required=True, type=int)

    opt_icinga_downtime = subparsers.add_parser('downtime-delete', help='Delete all Icinga downtimes.')

    return parser.parse_args()
