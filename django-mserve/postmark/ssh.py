########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-09-15
#	Created for Project :		Postmark
#
########################################################################
#
# Modified Code of paramiko (LGPL)
# https://github.com/robey/paramiko/blob/master/LICENSE
# to work around a bug when using paramiko in multithreaded applications
#
########################################################################
import logging
import getpass
import socket
from paramiko import Transport
from paramiko import SSHClient
from paramiko.common import *
from paramiko.resource import ResourceManager
from paramiko.ssh_exception import SSHException, BadHostKeyException
from paramiko.transport import Transport
SSH_PORT=22

class MultiTransport(Transport):

    def run(self):
        logging.info("MultiTransport r3d")
        from Crypto.Random import atfork
        atfork()
        super(MultiTransport, self).run()

class MultiSSHClient(SSHClient):

    def connect(self, hostname, port=SSH_PORT, username=None, password=None, pkey=None,
                key_filename=None, timeout=None, allow_agent=True, look_for_keys=True):
        """
        Connect to an SSH server and authenticate to it.  The server's host key
        is checked against the system host keys (see L{load_system_host_keys})
        and any local host keys (L{load_host_keys}).  If the server's hostname
        is not found in either set of host keys, the missing host key policy
        is used (see L{set_missing_host_key_policy}).  The default policy is
        to reject the key and raise an L{SSHException}.

        Authentication is attempted in the following order of priority:

            - The C{pkey} or C{key_filename} passed in (if any)
            - Any key we can find through an SSH agent
            - Any "id_rsa" or "id_dsa" key discoverable in C{~/.ssh/}
            - Plain username/password auth, if a password was given

        If a private key requires a password to unlock it, and a password is
        passed in, that password will be used to attempt to unlock the key.

        @param hostname: the server to connect to
        @type hostname: str
        @param port: the server port to connect to
        @type port: int
        @param username: the username to authenticate as (defaults to the
            current local username)
        @type username: str
        @param password: a password to use for authentication or for unlocking
            a private key
        @type password: str
        @param pkey: an optional private key to use for authentication
        @type pkey: L{PKey}
        @param key_filename: the filename, or list of filenames, of optional
            private key(s) to try for authentication
        @type key_filename: str or list(str)
        @param timeout: an optional timeout (in seconds) for the TCP connect
        @type timeout: float
        @param allow_agent: set to False to disable connecting to the SSH agent
        @type allow_agent: bool
        @param look_for_keys: set to False to disable searching for discoverable
            private key files in C{~/.ssh/}
        @type look_for_keys: bool

        @raise BadHostKeyException: if the server's host key could not be
            verified
        @raise AuthenticationException: if authentication failed
        @raise SSHException: if there was any other error connecting or
            establishing an SSH session
        @raise socket.error: if a socket error occurred while connecting
        """
        for (family, socktype, proto, canonname, sockaddr) in socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            if socktype == socket.SOCK_STREAM:
                af = family
                addr = sockaddr
                break
        else:
            raise SSHException('No suitable address family for %s' % hostname)
        sock = socket.socket(af, socket.SOCK_STREAM)
        if timeout is not None:
            try:
                sock.settimeout(timeout)
            except:
                pass
        sock.connect(addr)
        t = self._transport = MultiTransport(sock)

        if self._log_channel is not None:
            t.set_log_channel(self._log_channel)
        t.start_client()
        ResourceManager.register(self, t)

        server_key = t.get_remote_server_key()
        keytype = server_key.get_name()

        if port == SSH_PORT:
            server_hostkey_name = hostname
        else:
            server_hostkey_name = "[%s]:%d" % (hostname, port)
        our_server_key = self._system_host_keys.get(server_hostkey_name, {}).get(keytype, None)
        if our_server_key is None:
            our_server_key = self._host_keys.get(server_hostkey_name, {}).get(keytype, None)
        if our_server_key is None:
            # will raise exception if the key is rejected; let that fall out
            self._policy.missing_host_key(self, server_hostkey_name, server_key)
            # if the callback returns, assume the key is ok
            our_server_key = server_key

        if server_key != our_server_key:
            raise BadHostKeyException(hostname, server_key, our_server_key)

        if username is None:
            username = getpass.getuser()

        if key_filename is None:
            key_filenames = []
        elif isinstance(key_filename, (str, unicode)):
            key_filenames = [ key_filename ]
        else:
            key_filenames = key_filename
        self._auth(username, password, pkey, key_filenames, allow_agent, look_for_keys)
