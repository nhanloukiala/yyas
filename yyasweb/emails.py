__author__ = 'nhan'
from django.core.mail import EmailMessage

def sendMail(subject, content, receivers):
    if receivers is not None and len(receivers) > 0:
        mail = EmailMessage(subject, content, receivers)
        return mail.send()
    return -1
