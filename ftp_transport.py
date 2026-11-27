"""FTPS connection helpers for the remote exporter."""

# Bandit's ftplib rule also flags FTP_TLS; this module uses TLS for all traffic.
import ftplib  # nosec B402
import os
import socket
import ssl


FTP_MODE_FTPS_EXPLICIT = 'ftps_explicit'
FTP_MODE_FTPS_IMPLICIT = 'ftps_implicit'

FTP_AUTH_USER = 'user'
FTP_AUTH_ANONYMOUS = 'anonymous'

FTP_ERRORS = ftplib.all_errors
FTP_PERMISSION_ERROR = ftplib.error_perm
FTP_TLS = ftplib.FTP_TLS


class FTPLoginCancelled(Exception):
    """Raised when the user cancels the password prompt."""


class _ImplicitFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS variant which negotiates TLS before reading the server banner."""

    def connect(self, host='', port=0, timeout=None, source_address=None):
        if host:
            self.host = host
        if port:
            self.port = port
        if timeout is not None:
            self.timeout = timeout
        if source_address is not None:
            self.source_address = source_address
        if not self.host:
            raise ValueError('An FTP server hostname is required.')
        if self.timeout is not None and self.timeout == 0:
            raise ValueError('A zero FTP timeout is not supported.')

        raw_socket = socket.create_connection(
            (self.host, self.port), self.timeout,
            source_address=self.source_address)
        try:
            self.sock = self.context.wrap_socket(
                raw_socket, server_hostname=self.host)
        except Exception:
            raw_socket.close()
            raise

        try:
            self.af = self.sock.family
            self.file = self.sock.makefile('r', encoding=self.encoding)
            self.welcome = self.getresp()
        except Exception:
            self.close()
            raise
        return self.welcome


def default_port_for_mode(security_mode):
    if security_mode == FTP_MODE_FTPS_IMPLICIT:
        return 990
    if security_mode == FTP_MODE_FTPS_EXPLICIT:
        return 21
    raise ValueError('Unsupported FTP connection security mode.')


def security_mode_label(security_mode):
    labels = {
        FTP_MODE_FTPS_EXPLICIT: 'FTPS with explicit TLS',
        FTP_MODE_FTPS_IMPLICIT: 'FTPS with implicit TLS',
    }
    try:
        return labels[security_mode]
    except KeyError:
        raise ValueError('Unsupported FTP connection security mode.')


def create_ftp_client(security_mode, timeout=30):
    context = ssl.create_default_context()
    if security_mode == FTP_MODE_FTPS_EXPLICIT:
        return FTP_TLS(context=context, timeout=timeout)
    if security_mode == FTP_MODE_FTPS_IMPLICIT:
        return _ImplicitFTP_TLS(context=context, timeout=timeout)
    raise ValueError('Unsupported FTP connection security mode.')


def open_ftp_connection(host, port, security_mode, authentication_mode,
                        username, password_prompt, timeout=30):
    host = (host or '').strip()
    if not host:
        raise ValueError('Enter the FTP/FTPS server hostname.')
    port = int(port)
    if not 1 <= port <= 65535:
        raise ValueError('Enter a port between 1 and 65535.')

    if authentication_mode == FTP_AUTH_ANONYMOUS:
        login_username = 'anonymous'
    elif authentication_mode == FTP_AUTH_USER:
        login_username = (username or '').strip()
        if not login_username:
            raise ValueError('Enter the FTPS account username.')
    else:
        raise ValueError('Unsupported FTP login mode.')

    client = create_ftp_client(security_mode, timeout)
    try:
        client.connect(host, port, timeout=timeout)
        if security_mode == FTP_MODE_FTPS_EXPLICIT:
            client.auth()

        response = client.sendcmd('USER {}'.format(login_username))
        if response.startswith('331'):
            password = password_prompt()
            if password is None:
                raise FTPLoginCancelled()
            response = client.sendcmd('PASS {}'.format(password))

        if response.startswith('332'):
            raise ftplib.error_reply(
                '332 Server requires an FTP account (ACCT), which is not supported.')
        if response.startswith('3') or not response.startswith('2'):
            raise ftplib.error_reply(response)

        if security_mode in (FTP_MODE_FTPS_EXPLICIT, FTP_MODE_FTPS_IMPLICIT):
            client.prot_p()
        return client
    except BaseException:
        client.close()
        raise


def ensure_remote_directory(ftp, remote_folder):
    remote_folder = (remote_folder or '').strip().replace('\\', '/')
    if not remote_folder:
        return
    if remote_folder.startswith('/'):
        ftp.cwd('/')

    for part in remote_folder.split('/'):
        if not part or part == '.':
            continue
        if part == '..':
            ftp.cwd('..')
            continue
        try:
            ftp.cwd(part)
        except FTP_PERMISSION_ERROR:
            try:
                ftp.mkd(part)
            except FTP_PERMISSION_ERROR:
                pass
            ftp.cwd(part)


def upload_directory(ftp, local_folder, feedback, total_files):
    total_files = max(int(total_files), 1)
    uploaded = [0]

    def upload_tree(folder):
        if feedback.cancelled():
            return False
        with os.scandir(folder) as entries:
            items = sorted(entries, key=lambda entry: entry.name)

        for item in items:
            if feedback.cancelled():
                return False
            if item.is_file(follow_symlinks=False):
                with open(item.path, 'rb') as stream:
                    ftp.storbinary('STOR {}'.format(item.name), stream)
                uploaded[0] += 1
                progress = min(100, int(100 * uploaded[0] / total_files))
                feedback.setProgress(progress)
            elif item.is_dir(follow_symlinks=False):
                remote_parent = ftp.pwd()
                try:
                    try:
                        ftp.mkd(item.name)
                    except FTP_PERMISSION_ERROR:
                        pass
                    ftp.cwd(item.name)
                    if not upload_tree(item.path):
                        return False
                finally:
                    ftp.cwd(remote_parent)
        return True

    return upload_tree(local_folder)
