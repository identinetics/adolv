import logging
import ldap3

from classes.config import Config,ConfigErrorException
from classes.ldap import Ldap, LdapErrorException, TestFailedException
from ldap3.utils.log import set_library_log_detail_level, set_library_log_activation_level, OFF, BASIC, NETWORK, EXTENDED

try:
    config = Config()

except ConfigErrorException as e:
    print ("ERROR: Configuration error: {} ".format(e))
    quit()

if config.args.log:
    logging.basicConfig(filename='ldap.log', level=logging.DEBUG)
    set_library_log_activation_level(logging.DEBUG)
    set_library_log_detail_level(EXTENDED)

try:
    ldap = Ldap(test_config=config.test_config)
    ldap.run_test()
except LdapErrorException as e:
    print ("ERROR: {}".format(e))
    quit()
except TestFailedException as e:
    print ("FAILED")
    print (e)
    quit()

print ("OK")
quit()

