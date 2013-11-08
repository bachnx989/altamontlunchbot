__author__ = 'Simon'

import email
from bs4 import BeautifulSoup
import re


class Mail(object):

    def __init__(self,mail_string):
        print(type(mail_string))
        self.mail = email.message_from_string(mail_string)

    def get_text(self):

        if self.mail.is_multipart(): # Fancy data, most likely an attachment.
            try:
                attachment = self.get_attachment()
                text = attachment.read() # The attachment is a text file. Read it and save it to a string
                attachment.close() # Close the file. It's going to get overwritten and things could get very messy.
                return text
            except UnboundLocalError:
                print('Attachment does not exist!')

            try:
                text_raw = self.get_html_as_text()
                if 'Multimedia Message' in text_raw:
                    text = re.findall('Multimedia Message[ \n\t\r]+(.+?)[ \n\t\r]*$',text_raw,flags=re.DOTALL)
                else:
                    text = re.findall('^[ \n\t\r]+(.+?)[ \n\t\r]*$',text_raw,flags=re.DOTALL)
                return text[0]
            except UnboundLocalError:
                print('HTML does not exist! No readable parts found!')

        else:
            text = self.mail.get_payload()
        return text

    def get_attachment(self,attachment_type='text/plain'):

        for part in self.mail.walk():
            ctype = part.get_content_type()
            if ctype == attachment_type:
                open(part.get_filename(), 'wb').write(part.get_payload(decode=True)) # Drop the attachment to a file
                attachment = open(part.get_filename(),'r') # Grab a file handle for the dropped attachment
                break

        return attachment # return the handle.

    def get_html_as_text(self):
        for part in self.mail.walk():
            ctype = part.get_content_type()
            if ctype == 'text/html':
                part_soup = BeautifulSoup(part.get_payload())
                raw_text = part_soup.get_text()
                break
        return raw_text
