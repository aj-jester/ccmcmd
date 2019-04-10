import base64
import json
import re
import texttable

import ccmlog
import cliopts
import config
import helper
from requests_api import RequestsApi

def __consul_call(cliargs, configread):

    try:
        consul_call = RequestsApi(
            configread['consul']['location'][cliargs.location]['url'],
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Consul-Token': configread['consul']['location'][cliargs.location]['token'],
            }
        )

        return consul_call

    except KeyError, exc:
        if configread['consul']['location'].has_key(cliargs.location) is False:
            ccmlog.error("Location {} not found in config for consul.".format(exc))
        else:
            ccmlog.error("Consul call KeyError: {}.".format(exc))


def __get_all_keysvals(cliargs, configread, app_keyval=None):

    if app_keyval == 'all':
        kv_base_path = '/kv/'
        ccmlog.debug("App KeyVal: all, KV base path: {}".format(kv_base_path))
    elif app_keyval is not None:
        kv_base_path = "/kv/{}/node/".format(app_keyval)
        ccmlog.debug("App KeyVal: {}, KV base path: {}".format(app_keyval, kv_base_path))
    elif cliargs.app:
        kv_base_path = "/kv/{}/node/".format(cliargs.app)
        ccmlog.debug("App Cli: {}, KV base path: {}".format(cliargs.app, kv_base_path))
    else:
        kv_base_path = '/kv/'
        ccmlog.debug("App: None, KV base path: {}".format(kv_base_path))

    consul_kv_resp = __consul_call(cliargs, configread).get(kv_base_path, params={ 'recurse': True })

    if consul_kv_resp.status_code == 200:
        return consul_kv_resp.json()

    elif consul_kv_resp.status_code == 404:
        ccmlog.error("No keys found for fqdn {} in app {}. Its a 404.".format(cliargs.fqdn, cliargs.app))

    else:
        ccmlog.error("Error communicating with consul. HTTP status code {}.".format(consul_kv_resp.status_code))

def __get_all_hosts(cliargs, configread, keyval_all, filter_re=None):

    hosts = {}

    for keyval in keyval_all:

        # Decoded Value
        if keyval['Value'] is not None:
            decoded_value = base64.b64decode(keyval['Value'])
        else:
            ccmlog.error("None returned for key {}.".format(keyval['Key']))

        app_key, fqdn_key, usable_key = helper.key_split(keyval['Key'])

        match_key   = False
        match_value = False

        if cliargs.fqdn == 'all' or re.match(r"{}".format(cliargs.fqdn), fqdn_key):
            if filter_re is None:
                match_key = True

            else:
                if cliargs.filter_col == 'key':
                    match_key = re.search(r"{}".format(filter_re), usable_key, flags=re.IGNORECASE)
                elif cliargs.filter_col == 'value':
                    match_value = re.search(r"{}".format(filter_re), decoded_value, flags=re.IGNORECASE)
                else:
                    match_key = re.search(r"{}".format(filter_re), usable_key, flags=re.IGNORECASE)
                    match_value = re.search(r"{}".format(filter_re), decoded_value, flags=re.IGNORECASE)

        if match_key or match_value:

            if hosts.has_key(fqdn_key) is False:
                hosts[fqdn_key] = {}

            if hosts[fqdn_key].has_key(app_key) is False:
                hosts[fqdn_key][app_key] = {}

            hosts[fqdn_key][app_key][usable_key] = decoded_value

    if bool(hosts):
        return hosts
    else:
        ccmlog.error('No keys found.')

def keyval_get(cliargs, configread):

    keyval_all = __get_all_keysvals(cliargs, configread)
    filter_re  = "{}".format(cliargs.filter_re) if cliargs.filter_re else None
    hosts      = __get_all_hosts(cliargs, configread, keyval_all, filter_re)

    for fqdn, app in hosts.iteritems():

        for app_name, app_data in app.iteritems():
            tt = texttable.Texttable()
            tt.set_cols_align(["l", "l"])
            tt.set_cols_valign(["m", "m"])
            tt.set_cols_width([configread['consul']['common']['cols_width_key'], configread['consul']['common']['cols_width_val']])
            hoststt = []

            hoststt += [["App: {}".format(app_name), "FQDN: {}".format(fqdn)]]
            hoststt += [['KEY', 'VALUE']]

            for app_key, app_val in app_data.iteritems():
                hoststt += [[app_key, app_val]]

            tt.add_rows(hoststt)
            print tt.draw()

    ccmlog.info("Total FQDNs found: {}".format(len(hosts)))

def keyval_put(cliargs, configread):

    helper.no_leading_trailing_slashes(cliargs.key)

    # Apps that are immutable (set via config file) cannot be put.
    if cliargs.app in configread['consul']['common']['kv_apps_immutable']:
        ccmlog.error("Sorry {}, app {} in immutable, it's read only.".format(helper.ccmuser(),cliargs.app))

    # Add key if the host is in Facter app
    facter_keyval = __get_all_keysvals(cliargs, configread, app_keyval = 'facter')
    facter_hosts  = list(__get_all_hosts(cliargs, configread, facter_keyval).keys())

    if cliargs.fqdn in facter_hosts:
        key_sub_path = "/kv/{}/node/{}/{}".format(cliargs.app, cliargs.fqdn, cliargs.key)

        consul_kv_resp = __consul_call(cliargs, configread).put(key_sub_path, data=cliargs.value)

        if consul_kv_resp.status_code == 200 and consul_kv_resp.json() == True:
            ccmlog.info("Successfully put key {} in app {} for fqdn {}.".format(cliargs.key, cliargs.app, cliargs.fqdn))
            ccmlog.debug("Put value: {}".format(cliargs.value))
            ccmlog.debug("HTTP Status Code: {}".format(consul_kv_resp.status_code))
        else:
            ccmlog.debug("{}".format(vars(consul_kv_resp)))
            ccmlog.error("Consul HTTP Status Code: {}".format(consul_kv_resp.status_code))

    else:
        ccmlog.error("{} fqdn is not found.".format(cliargs.fqdn))

def __call_consul_delete(cliargs, configread, key_sub_path):

    consul_kv_resp = __consul_call(cliargs, configread).delete("/kv/{}".format(key_sub_path), params={ 'recurse': True })

    if consul_kv_resp.status_code == 200 and consul_kv_resp.json() == True:
        ccmlog.info("Successfully deleted key path {}".format(key_sub_path))
        ccmlog.debug("HTTP Status Code: {}".format(consul_kv_resp.status_code))
    else:
        ccmlog.debug("{}".format(vars(consul_kv_resp)))
        ccmlog.error("Consul HTTP Status Code: {}".format(consul_kv_resp.status_code))

def keyval_delete(cliargs, configread):

    # Apps that are immutable (set via config file) cannot be put.
    if cliargs.app in configread['consul']['common']['kv_apps_immutable']:
        ccmlog.error("Sorry {}, app {} is immutable, it's read only.".format(helper.ccmuser(),cliargs.app))

    # Add key if the host is in Facter app
    facter_keyval = __get_all_keysvals(cliargs, configread, app_keyval = 'facter')
    facter_hosts  = list(__get_all_hosts(cliargs, configread, facter_keyval).keys())

    if cliargs.fqdn in facter_hosts:

        if cliargs.app is None and cliargs.key:
            ccmlog.error("Must provide --app when using --key.")

        elif cliargs.app and cliargs.key:
            helper.no_leading_trailing_slashes(cliargs.key)
            key_sub_path = "{}/node/{}/{}".format(cliargs.app, cliargs.fqdn, cliargs.key)

            helper.prompt_to_verify(cliargs.key, cliargs.force)
            __call_consul_delete(cliargs, configread, key_sub_path)

        elif cliargs.app and configread['consul']['common']['kv_apps_mass_delete'] is True:
            key_sub_path = "{}/node/{}".format(cliargs.app, cliargs.fqdn)

            helper.prompt_to_verify("{}:{}".format(cliargs.fqdn, cliargs.app), cliargs.force)
            __call_consul_delete(cliargs, configread, key_sub_path)

        else:
            if configread['consul']['common']['kv_apps_mass_delete'] is True:
                kv_apps_deletable = list(set(configread['consul']['common']['kv_apps_available']) - set(configread['consul']['common']['kv_apps_immutable']))

                helper.prompt_to_verify("{}:mass-delete-keys".format(cliargs.fqdn), cliargs.force)

                for app in kv_apps_deletable:
                    key_sub_path = "{}/node/{}".format(app, cliargs.fqdn)
                    __call_consul_delete(cliargs, configread, key_sub_path)
            else:
                ccmlog.error("Mass delete set to {}. Plese provide a specific key to delete.".format(configread['consul']['common']['kv_apps_mass_delete']))

    else:
        ccmlog.error("{} fqdn is not found.".format(cliargs.fqdn))
