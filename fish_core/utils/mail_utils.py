import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


class SmtpKeys(object):
    SMTP_HOST = 'smtp_host'
    SMTP_PORT = 'smtp_port'
    SMTP_SENDER = 'smtp_sender'
    SMTP_RECEIVER = 'smtp_receiver'
    SMTP_SUBJECT = 'smtp_subject'
    SMTP_USERNAME = 'smtp_username'
    SMTP_PASSWORD = 'smtp_password'
    SMTP_ATTACHMENTS = 'smtp_attachments'
    SMTP_IS_THIRD_PARTY = 'smtp_third_party'
    SMTP_IS_SEND_HTML = 'smtp_send_html'
    SMTP_IS_SSL = 'smtp_ssl'
    SMTP_IS_VERBOSE_LOG = 'smtp_verbose_log'


class SmtpHelper(object):
    """
    The class represents an object for simplifying use operate in
    python email module and provides chaining invoke style for config.

    Usage:
    a = Attachment('E:\\test.jpg', 'test.jpg', 'image', 'jpg')

    helper = SmtpHelper() \
                .with_server('smtp.xx.com', 25) \
                .with_third_party_service() \
                .with_ssl() \
                .with_server_login('test@xxx.com', 'xxxxxxxxxxx') \
                .with_sender('SylvanasSun', 'test@xxx.com') \
                .with_receiver('Claude Shannon', ['123456@xxx.com']) \
                .with_subject('Hello') \
                .with_attachment(a)
    helper.send('Hello, World')

    Author: SylvanasSun <sylvanas.sun@gmail.com>
    Licence: MIT
    """

    def __init__(self):
        self.params = {}

    def with_server(self, host, port=25):
        if not isinstance(host, str) or not isinstance(port, int):
            raise ValueError('The type of host and port must be a string and integer')
        self.params[SmtpKeys.SMTP_HOST] = host
        self.params[SmtpKeys.SMTP_PORT] = port
        return self

    def with_server_login(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError('The type of username and password must be a string')
        self.params[SmtpKeys.SMTP_USERNAME] = username
        self.params[SmtpKeys.SMTP_PASSWORD] = password
        return self

    def with_sender(self, sender, addr):
        if not isinstance(sender, str) or not isinstance(addr, str):
            raise ValueError('The type of sender and address must be a string')
        self.params[SmtpKeys.SMTP_SENDER] = [sender, addr]
        return self

    def with_receiver(self, receiver, addr):
        if not isinstance(receiver, str):
            raise ValueError('The type of receiver must be a string')
        if not isinstance(addr, list):
            raise ValueError('The type of receiver address must be a list')
        self.params[SmtpKeys.SMTP_RECEIVER] = [receiver, addr]
        return self

    def with_subject(self, subject):
        if not isinstance(subject, str):
            raise ValueError('The type of subject must be a string')
        self.params[SmtpKeys.SMTP_SUBJECT] = subject
        return self

    def with_third_party_service(self):
        self.params[SmtpKeys.SMTP_IS_THIRD_PARTY] = True
        return self

    def with_send_html(self):
        self.params[SmtpKeys.SMTP_IS_SEND_HTML] = True
        return self

    def with_ssl(self):
        self.params[SmtpKeys.SMTP_IS_SSL] = True
        return self

    def with_verbose_log(self):
        self.params[SmtpKeys.SMTP_IS_VERBOSE_LOG] = True
        return self

    def with_attachment(self, attachments):
        if not isinstance(attachments, Attachment) and not isinstance(attachments, list):
            raise ValueError('The type of attachments must be a class Attachment or list')
        elif isinstance(attachments, list):
            for a in attachments:
                if not isinstance(a, Attachment):
                    raise ValueError('The type of attachments must be a class Attachment')

        self.params[SmtpKeys.SMTP_ATTACHMENTS] = attachments
        return self

    def send(self, message_body, encode_format='utf-8'):
        self._validate_necessary_metadata([SmtpKeys.SMTP_HOST,
                                           SmtpKeys.SMTP_PORT,
                                           SmtpKeys.SMTP_SUBJECT,
                                           SmtpKeys.SMTP_SENDER,
                                           SmtpKeys.SMTP_RECEIVER])
        message, from_addr, to_addr = self._build_message(message_body, encode_format)
        smtp_server = self._build_smtp_server()
        try:
            smtp_server.sendmail(from_addr, to_addr, message.as_string())
        finally:
            smtp_server.quit()

    def _build_message(self, message_body, encode_format):
        msg = MIMEMultipart()
        sender = self.params[SmtpKeys.SMTP_SENDER]
        msg['From'] = self._format_addr('%s <%s>' % (sender[0], sender[1]), encode_format)

        receiver = self.params[SmtpKeys.SMTP_RECEIVER]
        if len(receiver[1]) == 1:
            msg['To'] = self._format_addr('%s <%s>' % (receiver[0], receiver[1]), encode_format)
        else:
            msg['To'] = self._format_addr(receiver[0], encode_format)

        msg['Subject'] = Header(self.params[SmtpKeys.SMTP_SUBJECT], encode_format).encode()

        if self._validated(SmtpKeys.SMTP_IS_SEND_HTML):
            msg.attach(MIMEText(message_body, 'html', encode_format))
        else:
            msg.attach(MIMEText(message_body, 'plain', encode_format))

        if SmtpKeys.SMTP_ATTACHMENTS in self.params:
            attachments = self.params[SmtpKeys.SMTP_ATTACHMENTS]
            if isinstance(attachments, list):
                for a in attachments:
                    msg.attach(a.to_MIME())
            else:
                msg.attach(attachments.to_MIME())

        return msg, sender[1], receiver[1]

    def _build_smtp_server(self):
        if self._validated(SmtpKeys.SMTP_IS_SSL):
            smtp = smtplib.SMTP_SSL(self.params[SmtpKeys.SMTP_HOST], self.params[SmtpKeys.SMTP_PORT])
        else:
            smtp = smtplib.SMTP(self.params[SmtpKeys.SMTP_HOST], self.params[SmtpKeys.SMTP_PORT])

        if self._validated(SmtpKeys.SMTP_IS_THIRD_PARTY):
            if SmtpKeys.SMTP_USERNAME in self.params and SmtpKeys.SMTP_PASSWORD in self.params:
                smtp.login(self.params[SmtpKeys.SMTP_USERNAME], self.params[SmtpKeys.SMTP_PASSWORD])

        if self._validated(SmtpKeys.SMTP_IS_VERBOSE_LOG):
            smtp.set_debuglevel(1)

        return smtp

    def _format_addr(self, s, encode_format='utf-8'):
        name, addr = parseaddr(s)
        return formataddr((Header(name, encode_format).encode(), addr))

    def _validated(self, key):
        return key in self.params and self.params[key]

    def _validate_necessary_metadata(self, keys):
        for key in keys:
            if key not in self.params:
                raise ValueError('The value %s must be exist' % key)


class Attachment(object):
    """
    The class represent an object that comprises necessary metadata of
    one attachment and provides a function for convert to MIMEBase
    """

    def __init__(self, path, filename, maintype, subtype, id=None):
        self.path = path
        self.filename = filename
        self.maintype = maintype
        self.subtype = subtype
        self.id = id

    def to_MIME(self):
        mime = MIMEBase(self.maintype, self.subtype, filename=self.filename)
        mime.add_header('Content-Disposition', 'attachment', filename=self.filename)
        if self.id is not None:
            mime.add_header('Content-ID', '<%s>' % self.id)
            mime.add_header('X-Attachment-Id', str(self.id))
        with open(self.path, 'rb') as f:
            mime.set_payload(f.read())
        encoders.encode_base64(mime)
        return mime
