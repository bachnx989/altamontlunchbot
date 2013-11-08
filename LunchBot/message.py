__author__ = 'Simon'

import email

class Attachment(object):

    def __init__(self,msg_part):
        open(msg_part.get_filename(), 'wb').write(msg_part.get_payload(decode=True))
        self.data = open(msg_part.get_filename(),'r').read()
        self.data_type = msg_part.get_content_type()
        self.file_name = msg_part.get_filename()

    def __str__(self):
        return self.data

class Body(object):

    def __init__(self,msg_part):
        self.body = msg_part.get_payload(decode=True)

    def __str__(self):
        return self.body



def parse_attachment(msg_part):
    content_disposition = msg_part.get("Content-Disposition", None)
    if content_disposition: #
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and dispositions[0].lower() == "attachment"):
            attachment = Attachment(msg_part)
            return attachment
    return None

def parse_body(msg_part):
    body = msg_part.get_payload(decode=True)
    return body

def parse_mail(mail):
    attachments = []
    body = None
    for part in mail.walk():
        attachment = parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type == 'text/plain':
            if not body:
                body = Body(part)
    if len(attachments) != 0:
        return attachments
    return body
