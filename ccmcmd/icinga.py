import time
import socket

import ccmlog
import helper

def downtime_set(cliargs, configread):

    if cliargs.hours > configread['icinga']['common']['downtime_max_hours']:
        ccmlog.error("Sorry {}, cannot set downtime to {} hrs, its greater than {} hrs.".format(helper.ccmuser(), cliargs.hours, configread['icinga']['common']['downtime_max_hours']))

    data = {}
    data['host_name'] = cliargs.fqdn
    data['start_time'] = int(time.time())
    data['end_time'] = data['start_time'] + (cliargs.hours * 3600)
    data['author'] = helper.ccmuser()
    data['comment'] = "Setting downtime for {} hrs via ccmcmd.".format(cliargs.hours)
    data['trigger_id'] = 0
    data['fixed'] = 1
    data['duration'] = cliargs.hours * 3600

    sock = socket.socket()
    try:
        sock.connect((configread['icinga']['location'][cliargs.location]['livestatus_host'], configread['icinga']['location'][cliargs.location]['livestatus_port']))
        cmd = '''COMMAND [%(start_time)s] SCHEDULE_HOST_SVC_DOWNTIME;''' \
              '''%(host_name)s;%(start_time)s;%(end_time)s;%(fixed)s''' \
              ''';%(trigger_id)s;%(duration)s;%(author)s;%(comment)s''' \
              '''\n\n''' % data

        sock.send(cmd)
        sock.shutdown(socket.SHUT_WR)

        ccmlog.info("Downtime set for host {} for {} hrs.".format(cliargs.fqdn, cliargs.hours))
        ccmlog.debug("Set by user: {}".format(helper.ccmuser()))

    except socket.error, exc:
        ccmlog.error("Error connecting to Icinga: {}".format(exc))

    except KeyError, exc:
        if configread['icinga']['location'].has_key(cliargs.location) is False:
            ccmlog.error("Location {} not found in config for icinga.".format(exc))
        else:
            ccmlog.error("Icinga downtime-set call KeyError: {}.".format(exc))

def downtime_delete(cliargs, configread):

    data = {}
    data['host_name'] = cliargs.fqdn
    data['start_time'] = int(time.time())

    sock = socket.socket()
    try:
        sock.connect((configread['icinga']['location'][cliargs.location]['livestatus_host'], configread['icinga']['location'][cliargs.location]['livestatus_port']))
        cmd = '''COMMAND [%(start_time)s] DEL_DOWNTIME_BY_HOST_NAME;''' \
              '''%(host_name)s''' \
              '''\n\n''' % data

        sock.send(cmd)
        sock.shutdown(socket.SHUT_WR)

        ccmlog.info("Downtime deleted for host {}.".format(cliargs.fqdn))
        ccmlog.debug("Deleted by user: {}".format(helper.ccmuser()))

    except socket.error, exc:
        ccmlog.error("Error connecting to Icinga: {}".format(exc))

    except KeyError, exc:
        if configread['icinga']['location'].has_key(cliargs.location) is False:
            ccmlog.error("Location {} not found in config for icinga.".format(exc))
        else:
            ccmlog.error("Icinga downtime-delete call KeyError: {}.".format(exc))
