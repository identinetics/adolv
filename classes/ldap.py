import ldap3
import ssl
import re
import ast
import pprint
import collections

class LdapErrorException(Exception):
    def __init__(self, message=None, errors=None):
        super(LdapErrorException, self).__init__(message)
        self.errors = errors

class TestFailedException(Exception):
    def __init__(self, message=None, errors=None):
        super(TestFailedException, self).__init__(message)
        self.errors = errors

class TargetUser(object):
    def __init__(self,entry):
        self.entry = entry

    def dn(self):
        return str(self.entry.distinguishedName)


class Ldap(object):
    def __init__(self,config):
        self.config = config

    def run_test(self):
        self._test_connect()
        self._test_naming_contexts()
        self._test_search_user()
        if self.config.args.dump_entry:
            self._dump_user_data()
        self._test_target_user_login(password=self.config.test_config.test_target_user_pw, exception_prefix='first login')
        self._test_password_change()
        self._test_target_user_login(password=self.config.test_config.test_target_tmp_pw, exception_prefix='second login')
        self._test_password_change(restore=True)
        return

    def _dump_user_data(self):
        ordered_dict = collections.OrderedDict(self.target_user.__dict__)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(ordered_dict)
        return

    def _test_password_change(self, restore=False):
        dn = self.target_user.dn()

        if restore:
            new_password = self.config.test_config.test_target_user_pw
            exception_prefix = 'password restore failed: '
        else:
            new_password = self.config.test_config.test_target_tmp_pw
            exception_prefix = 'set password failed: '

        try:
            ldap3.extend.microsoft.modifyPassword.ad_modify_password(
                self.connection, dn, new_password, None,  controls=None)
        except Exception as e:
            raise TestFailedException(exception_prefix+str(e))

    def _test_target_user_login(self,password='not set',exception_prefix='login'):
        dn = self.target_user.dn()
        try:
            test_conn = ldap3.Connection(self.server, user=dn, password=password,
                                     auto_bind=True, client_strategy=ldap3.SYNC, authentication=ldap3.SIMPLE)
        except ldap3.core.exceptions.LDAPBindError as e:
            msg = "{} failed for {}: {}".format(exception_prefix,dn,e)
            raise TestFailedException(msg)
        return

    def _test_search_user(self):
        dn = self.config.test_config.test_target_base_dn
        f = self.config.test_config.test_target_user_filter
        try:
            self.connection.search(  search_base=dn,
                          search_filter=f ,
                          dereference_aliases=ldap3.DEREF_NEVER,
                          search_scope=ldap3.SUBTREE,
                          attributes=["*" ])
        except (ldap3.core.exceptions.LDAPInvalidFilterError,
                ldap3.core.exceptions.LDAPObjectClassError) as e:
            raise LdapErrorException(e)

        number_of_entries_found = len(self.connection.entries)
        if number_of_entries_found == 1:
            self.target_user = TargetUser(self.connection.entries[0])
            return

        if len(self.connection.entries) < 1:
            msg_card = 'no entry'
        else:
            msg_card = 'more than one entry'
        msg = "the search returned {}, but should return one user entry. Used filter: {}, BaseDN: {}".format(
            msg_card, f, dn)

        raise TestFailedException(msg)

    def _test_connect(self):

        try:
            if self.config.test_config.cacert or self.config.test_config.cacertpath:
                tls = ldap3.Tls(
                    validate=ssl.CERT_REQUIRED,
                    ca_certs_file=self.config.test_config.cacert,
                    ca_certs_path=self.config.test_config.cacertpath,
                    valid_names=self.config.test_config.alt_names
                )
            else:
                tls = ldap3.Tls(validate=ssl.CERT_NONE)
        except ldap3.core.exceptions.LDAPSSLConfigurationError as e:
            raise LdapErrorException(e)

        self.server = ldap3.Server(
            host=self.config.test_config.host,
            port=636,
            use_ssl=True,
            tls=tls,
            get_info=ldap3.ALL)
        try:
            self.connection = ldap3.Connection(
                self.server,
                self.config.test_config.admin_user,
                password=self.config.test_config.admin_pw,
                auto_bind=True,
                client_strategy=ldap3.SYNC)
        except ldap3.core.exceptions.LDAPBindError as e:
            raise LdapErrorException(e)
        except ldap3.core.exceptions.LDAPSocketOpenError as e:
            cert_error = self.__parse_certificate_error(e)
            if cert_error:
                raise LdapErrorException(cert_error)
            raise LdapErrorException(e)

        return

    def __parse_certificate_error(self,exception):
        message = str(exception)
        match = re.match(r"socket ssl wrapping error: certificate {(.*)} .* in \[(.*)\]",
                     message,
                     re.IGNORECASE)
        if match:
            cert_str = "{" + match.group(1) + "}"
            cert = ast.literal_eval(cert_str)
            cert_subject= str(cert['subject'])
            names_str = "[" + match.group(2) + "]"
            names = ast.literal_eval(names_str)
            names_joined = ",".join(names)
            msg = "certificate error: subject does not match hostnames: {} subject: {}".format(names_joined,cert_subject)
            return msg
        else:
            return False

    def _test_naming_contexts(self):
        if self.config.test_config.test_target_base_dn not in self.server.info.naming_contexts:
            r = ["the AD server does not have the naming context for {}".format(
                self.config.test_config.test_target_base_dn)]
            r.append("supported naming contexts are:")
            r = r + self.server.info.naming_contexts
            msg = "\n".join(r)
            raise TestFailedException(msg)
        return


