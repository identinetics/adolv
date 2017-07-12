import argparse
import configparser

class ConfigErrorException(Exception):
    def __init__(self, message=None, errors=None):
        super(ConfigErrorException, self).__init__(message)
        self.errors = errors

class CmdlineArgs(object):
    def __init__(self,config,test=None,log=False):
        self.config = config
        self.test = test
        self.log = log

    def __repr__(self):
        r = []
        r.append(super(CmdlineArgs,self).__repr__())
        r.append("config={}, test={}, log={}".format(self.config,self.test, self.log))
        return "\n".join(r)

class ConfigFile(object):
    def __init__(self,filename):
        self.filename = filename
        self.config = configparser.ConfigParser()
        files_read = self.config.read(self.filename)
        if not files_read:
            msg = "config file \"{}\" could not be processed".format(self.filename)
            raise ConfigErrorException(msg)

    def __repr__(self):
        r = []
        r.append(super(ConfigFile,self).__repr__())
        r.append("filename: {}".format(self.filename))
        return "\n".join(r)

class TestConfig(object):
    def __init__(self,test_name,config_file):
        self.test_name = test_name
        self.config_file = config_file

        self.alt_names = []
        try:
            self.host = config_file.config.get(self.test_name,'Host')
            self.cacert = config_file.config.get(self.test_name, 'Cacert', fallback=None)
            self.alt_names_txt = config_file.config.get(self.test_name, 'AltNames', fallback=None)
            if self.alt_names_txt:
                alt_names = self.alt_names_txt.split(',')
                for n in alt_names:
                    self.alt_names.append(n.strip())
            self.admin_user = config_file.config.get(self.test_name,'AdminUser')
            self.admin_pw = config_file.config.get(self.test_name,'AdminPw')
            self.test_target_base_dn = config_file.config.get(self.test_name,'BaseDn')
            self.test_target_user_filter = config_file.config.get(self.test_name,'Filter')
            self.test_target_user_pw = config_file.config.get(self.test_name,'UserPw')
            self.test_target_tmp_pw = config_file.config.get(self.test_name,'ChangePw')
        except configparser.NoOptionError as e:
            raise ConfigErrorException('a option is missing: '+str(e))



    def __str__(self):
        r = []
        r.append("Host: {}".format(self.host))
        r.append("Adminuser: {}".format(self.admin_user))
        r.append("BaseDn: {}".format(self.test_target_base_dn))
        r.append("Filter: {}".format(self.test_target_user_filter))
        return ", ".join(r)


    def __repr__(self):
        r = []
        r.append(super(TestConfig,self).__repr__())
        r.append(self.__str__())
        return "\n".join(r)



class Config(object):

    def __init__(self):
        self.cmdline_args = None
        self.config_file = None
        self.test_config = None
        self.parser = None
        self.args = None
        self.selected_test = None
        self.__parser()
        self.__parse_args()
        self.__read_config_file()

    def __parser(self):
        self.parser = argparse.ArgumentParser(
            description="Test password change on a MSFT AD",
            epilog="example: %(prog)s -c config.conf",
            usage='%(prog)s [options]',
            prog='testAdLdap'
        )
        self.parser.add_argument('-c', '--conf', dest='config', default='tests.conf',
                    help='test config file')
        self.parser.add_argument('-t', '--test', dest='test',
            help='selects the test in case more than one is defined in the config file')
        self.parser.add_argument('-l', '--log', dest='log', action='store_true',
            help='write a ldap log to the file "ldap.log"')
        self.parser.add_argument('-d', '--dump-entry', dest='dump_entry', action='store_true',
                                 help='print the person entry')
        self.parser.set_defaults(log=False)
 
    def __parse_args(self):
        self.args = self.parser.parse_args()
        self.cmdline_args = CmdlineArgs(self.args.config, self.args.test, self.args.log)

    def __read_config_file(self):
        self.config_file = ConfigFile(self.cmdline_args.config)
        tests_list = self.config_file.config.sections()
        if not tests_list:
            raise ConfigErrorException("No test was found in this config")
        if self.cmdline_args.test:
            if self.cmdline_args.test in tests_list:
                self.selected_test = self.cmdline_args.test
            else:
                raise ConfigErrorException("the test \"{}\" was not found. Available tests in this config: {}".format(
                    self.cmdline_args.test, ",".join(tests_list)))
        else:
            self.selected_test = tests_list[0]

        self.test_config = TestConfig(self.selected_test,self.config_file)

    def __repr__(self):
        r = []
        r.append(super(Config,self).__repr__())
        if not self.parser or not self.args:
            r.append("Not initialized")
        else:
            r.append(str(self.args))
            r.append(str(self.cmdline_args))
            r.append(str(self.config_file))
            r.append("selected test: \"{}\"".format(self.selected_test))
            r.append(str(self.test_config))
        return "\n".join(r)

