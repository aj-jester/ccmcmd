import os
import yaml

import ccmlog

def read():

    config_dirs = []

    if os.environ.has_key('CCMCMD_CONFIG_DIR'):
        ccmlog.debug("Using ENV variable CCMCMD_CONFIG_DIR: {}".format(os.environ['CCMCMD_CONFIG_DIR']))
        config_dirs += [os.environ['CCMCMD_CONFIG_DIR']]

    else:
        config_dirs += ['/opt/ccm/data', '/etc']

    for config_dir in config_dirs:
        config_file = "{}/ccmcmd.yaml".format(config_dir)
        ccmlog.debug("Searching dir {} for config file.".format(config_dir))

        if os.path.isfile(config_file):
            ccmlog.debug("Found config file: {}".format(config_file))
            active_file = config_file

            with open(active_file, 'r') as stream:
                try:
                    config_data = yaml.load(stream)
                    ccmlog.debug("Loaded config file: {}".format(config_file))

                    return config_data

                except yaml.YAMLError as exc:
                    ccmlog.error("Error reading config file {}: {}".format(active_file, exc))

            break

    else:
        ccmlog.error('No valid config file found.')
