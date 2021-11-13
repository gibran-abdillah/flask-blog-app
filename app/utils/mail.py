from email.mime.text import MIMEText
from re import sub
import smtplib
from email.mime.multipart import MIMEMultipart

class Mail:
    
    def __init__(self, app=None):
        self.app = app 
    
    def init_app(self, app):
        self.app = app 
        for keys, values in self.app.config.items():
            setattr(self, keys.lower(), values)
        self.smtp = self.connect()
        
    
    def connect(self):
        try:
            if self.mail_usessl:
                smtp = smtplib.SMTP_SSL(self.mail_host, self.mail_port)
            else:
                smtp = smtplib.SMTP(self.mail_host, self.mail_port)
            
            if self.mail_usetls:
                smtp.starttls()
            if self.mail_sender and self.mail_password:
                smtp.login(self.mail_sender, self.mail_password)
            return smtp
        except Exception as e:
            self.app.logger.error(
                'cant connect to smtp, '
                'reset password features cant be used'
            )
    
    def __enter__(self):
        if not self.app:
            raise RuntimeError('app not found in mail')
    
    def send_msg(self, msg):
        assert isinstance(msg, Message), 'msg params must be same as Message class'
        
        msg = msg.message_content()
        msg['From'] = self.mail_sender
        self.smtp.send_message(msg)

class Message:

    def __init__(self, 
                 to=False,
                 html=True, 
                 body=False,
                 subject=False):
        
        self.to = to or set()
        self.html = html 
        self.subject = subject
        self.body = body
        
    
    def message_content(self):
        """
        generate message content for send mail
        """
        assert self.to, 'reciptiens mail not found'
        assert self.subject, 'subject cant be empty'
        assert self.body, 'body email cant be empty'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject

        if type(self.to) == set:

            msg['To'] = ','.join(self.to)
        else:
            msg['To'] = self.to

        if self.html:
            tipe = MIMEText(self.body, 'html')
        else:
            tipe = MIMEText(self.body, 'text')
        
        msg.attach(tipe)
        return msg

    def add_recipients(self, recipients: str):
        self.to.add(recipients)
    