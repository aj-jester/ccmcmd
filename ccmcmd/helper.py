import os
import re

import ccmlog

# Find user running the package.
def ccmuser():
    if os.environ.has_key('SUDO_USER'):
        ccmlog.debug("Command being run as {}.".format(os.environ['SUDO_USER']))
        return os.environ['SUDO_USER']
    elif os.environ.has_key('USER'):
        ccmlog.debug("Command being run as {}.".format(os.environ['USER']))
        return os.environ['USER']
    else:
        ccmlog.error('Unable to find the user.')

# Keys should not have leading or trailing slashes.
def no_leading_trailing_slashes(key_name):
    if re.search(r'(^\/)|(\/$)', key_name):
        ccmlog.debug("Key name: {}".format(key_name))
        ccmlog.error('Keys should not have leading or trailing slashes.')

def key_split(key):
    # Format: [<app>, 'node' <fqdn>, <rest of the key...aka 'usable_name'>]
    # Ex: ['facter', 'node', 'tier-role-1.ops.loc1.domain.com', 'test/this/side']
    key_split = key.split('/', 3)

    app_key    = key_split[0]
    fqdn_key   = key_split[2]
    usable_key = key_split[3]

    return app_key, fqdn_key, usable_key

def prompt_to_verify(prompted_message, force=False):
    if force is False:
        while True:
            try:
                entered_response = str(raw_input("Please type \'{}\': ".format(prompted_message)))
            except ValueError:
                ccmlog.error('Invalid value, please try again.', exit=False)
                continue

            if entered_response == prompted_message:
                ccmlog.debug("Entered value \'{}\' matched prompted message \'{}\'.".format(entered_response, prompted_message))
                break

            else:
                ccmlog.error("Sorry, your response must be \'{}\'.".format(prompted_message), exit=False)
                continue
