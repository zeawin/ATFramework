# -*- coding: utf-8 -*-

"""
    Effect: 
"""

import re
import threading
import time
import os
import socket
import traceback
import paramiko
from paramiko import Transport
from paramiko.ssh_exception import SSHException, AuthenticationException
from Framework.Exception.ATException import ATException
from Framework import Log


class SSHConnection(object):
    logger = Log.getLogger(__name__)

    def __init__(self, ip, user, password=None, private_key=None, port=22):
        self.line_sep = '\n'
        self.status = None
        self.ip = ip
        self.user = user
        self.password = password
        self.private_key = private_key
        self.port = port
        self.prompt_dict = None
        self.transport = None
        self.channel = None
        self.local_param = threading.local()  # 线程本地变量，不同线程相互独立的变量

    def __del__(self):
        self.close()

    def create_sftp_client(self):
        transport = self.create_client()
        self.authentication(transport)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    def send(self, command, timeout=10):
        now = time.time()
        end = now + timeout
        while now < end:
            try:
                self.logger.debug('To execute command: \'%s\'' % command)
                self.channel.send(command + self.line_sep)
                return True
            except socket.timeout as e:
                self.logger.warn('Execute command: \'%s\' timeout.' % command)
                now = time.time()
            return False

    def receive(self, prompt='[>#]', n_bytes=None, timeout=120, last=None):
        if not self.isActive():
            raise ATException('Connection for [%s] has been closed' % self.ip)
        matchable = False
        match_str = None
        result = ''
        now = time.time()
        end = now + timeout
        warn_msg = ''
        while now < end:
            received = ''
            match = None
            try:
                received = self.channel.recv(n_bytes)
            except socket.timeout:
                if not warn_msg:
                    warn_msg = 'Connection is receiving result.'
                    self.logger.warn(warn_msg)
            if received:
                result += received
                matchable = re.search(prompt, result)
            if matchable:
                matchable = True
                match_str = match.group()
                break
            now = time.time()
        self.logger.debug('Got result: \n%s' % result)
        if result == '':
            result = None
        return result, matchable, match_str

    def create_client(self):
        count = 0
        while count < 3:
            try:
                ssh = paramiko.SSHClient()
                if self.private_key:
                    try:
                        key = paramiko.RSAKey.from_private_key_file(self.private_key)
                    except SSHException:
                        key = paramiko.DSSKey.from_private_key_file(self.private_key)
                    self.logger.debug('Login IP:[%s] with user:[%s], password:[%s], private key[%s]' %
                                      (self.ip, self.user, self.password, self.private_key))
                    ssh.connect(self.ip, self.port, username=self.user, pkey=key, timeout=10,
                                auth_timeout=10)

                else:
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(self.ip, self.port, password=self.password, timeout=10, auth_timeout=10)
                self.transport = ssh.get_transport()
                self.transport.set_keepalive(30)
                if not self.transport.is_active():
                    raise ATException('Start ssh connection error.')
                break
            except (socket.error, EOFError, paramiko.SSHException, ATException):
                self.logger.warn('Failed to connect to %s:%s' % (self.ip, self.port))
                count += 1
        else:
            raise ATException('Create connection to %s failed.' % self.ip)

    def authentication(self, transport):
        if not transport.is_authenticated():
            if self.private_key:
                self.auth_public_key(transport)
            elif self.password is not None:
                try:
                    self.auth_password(transport)
                except paramiko.BadAuthenticationType as e:
                    if 'keyboard-interactive' not in e.allowed_types:
                        raise ATException('authentication failed with password.')
                    self.auth_interactive(transport)
                    self.logger.debug('Login to %s success.' % self.ip)

    def auth_interactive(self, transport):
        self.logger.debug('Try to keyboard interactive authentication to %s.' % self.ip)

        def handler(title, instructions, fields):
            if len(fields) > 1:
                raise ATException('Fallback authentication failed.')
            elif len(fields) == 0:
                return []
            return [self.password]

        my_event = threading.Event()
        transport.auth_handler = paramiko.AuthHandler(transport)
        transport.auth_handler.auth_interactive(self.user, handler, my_event, '')
        my_event.wait(120)
        if not my_event.is_set():
            self.logger.warn('Timeout to authentication')
        if not transport.is_authenticated():
            error = transport.get_exception()
            if error is None:
                error = AuthenticationException('Authentication failed.')
                raise error

    def auth_password(self, transport):
        self.logger.debug('Try to password authentication to %s' % self.ip)
        my_event = threading.Event()
        transport.auth_password(self.ip, self.password, my_event)
        my_event.wait(120)
        if not my_event.is_set():
            self.logger.warn('Timeout to authentication')
        if not transport.is_authenticated():
            error = transport.get_exception()
            if error is None:
                error = AuthenticationException('Authentication failed.')
                raise error

    def auth_public_key(self, transport):
        self.logger.debug('Try to public key authentication to %s' % self.ip)
        my_event = threading.Event()
        try:
            key = paramiko.RSAKey.from_private_key_file(self.private_key)
        except SSHException:
            key = paramiko.DSSKey.from_private_key_file(self.private_key)
        transport.auth_publickey(self.user, key, my_event)
        my_event.wait(120)
        if not my_event.is_set():
            self.logger.warn('Timeout to authentication')
        if not transport.is_authenticated():
            error = transport.get_exception()
            if error is None:
                error = AuthenticationException('Authentication failed.')
                raise error

    def login(self):
        if not self.transport or self.transport.is_active():
            self.create_client()
        channel = self.transport.open_session()
        channel.get_pty(width=200, height=200)
        channel.invoke_shell()
        channel.settimeout(10)
        self.channel = channel
        result, matchable, match_str = self.receive(timeout=10)
        if not matchable:
            self.logger.warn('Has not got the command prompt yet at this connection.')
        default_prompt = '@#>'
        self.excute('PS1="\u@#>"', prompt=default_prompt, timeout=10)
        self.excute('LS_OPTIONS="-A -N"', prompt=default_prompt, timeout=10)
        self.prompt_dict['normal'] = default_prompt
        self.status = 'normal'

    def excute(self, command, prompt, timeout):
        self.send(command)
        return self.receive(prompt, timeout)
