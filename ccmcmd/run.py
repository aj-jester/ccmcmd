import ccmlog
import cliopts
import config
import consul
import icinga
import helper

def apps():

    helper.ccmuser()

    configread = config.read()
    cliargs = cliopts.args(configread)
    ccmlog.debug("Cli args: {}".format(vars(cliargs)))

    if cliargs.apps == 'consul':

        if cliargs.consul == 'keyval-get':
           consul.keyval_get(cliargs, configread)
        elif cliargs.consul == 'keyval-put':
           consul.keyval_put(cliargs, configread)
        elif cliargs.consul == 'keyval-delete':
           consul.keyval_delete(cliargs, configread)

    elif cliargs.apps == 'icinga':

        if cliargs.icinga == 'downtime-set':
            icinga.downtime_set(cliargs, configread)
        elif cliargs.icinga == 'downtime-delete':
            icinga.downtime_delete(cliargs, configread)

    else:
        ccmlog.error('Please choose an app. Should not be here, most definitely a bug.')
