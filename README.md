# ADOLV - Active Directory Over LDAP Verification

A tool to check administrative access to Microsoft Active Directory over LDAP from Linux/Python/ldap3.

## Purpose

Making it easier to connect to Microsoft Active Directory over LDAP from Linux for administrative tasks.

## Overview

The tool will try to change the password of a given test user account. It performs these operations:

 1. Connect to the Microsoft Active Directory using SSL and admin credentials.
 1. Perform a search for a given test user account
 1. Bind as this test user (password check)
 1. Change this users password to a temp. password
 1. Bind again, using the new password
 1. Change this users password back, to its original one

If something fails, -l will write a verbose log to ldap.log

## Usage

python adolv.py

### optional arguments:
|parameter| help |
|--|--|
|-h, --help | show this help message and exit |
|-c CONFIG, --conf CONFIG | config file. Default: tests.conf |
|-t TEST, --test TEST | elects the test in case more than one is defined in the config file |
|  -l, --log | write a ldap log to the file "ldap.log" |

## Configuration

Configuration is given by a win.ini style file, where each section is a test and can be selected with --test, in case more than one is defined in the config file.

```bash
[MyAD]
Host: MYAD-NAME.example.com
Cacert: certs/my_ca_root.pem
AdminUser: myad\Administrator
AdminPw: a_very_secret_admin_password

BaseDn: DC=myad,DC=emp,DC=example,DC=com
Filter: (&(objectclass=person)(sn=Foobar))

UserPw: FoobarsSecretPassword
ChangePw: MirkoS0ft
```

### Host

IP address or FQDN of the Microsoft Active Directory Server

### Cacert

Optional parameter.
CA certificate file in PEM encoding. If given, the SSL connection will be verified with this certificate.

### AdminUser, AdminPw

Credentials of the administrative user. Adminuser can be given in the form of `<Domain>\Administrator`.

### BaseDn, Filter

The base DN and filter for the search. The search should return only one user entry - which will be the one to be used for password changing.

### UserPw

The password of the user, returned by the search.

### ChangePw

The temporary password this user account will be changed to for testing.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```