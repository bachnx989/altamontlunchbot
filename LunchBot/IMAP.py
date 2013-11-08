__author__ = 'Simon'
from imapclient import IMAPClient

class IdleInterrupt(Exception):
    """
    Raised when an idle() action occurs.
    """
    def __init__(self):
        super(IdleInterrupt, self).__init__()



class IMAP_Connection(object):

    def __init__(self,host='imap.gmail.com',user='altamontlunchbot@gmail.com',pwd='lunchbotpassword',port=993,ssl=True,folder='INBOX'):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.ssl = ssl
        self.folder = folder
        self.conn = self.start_connection()
        self.conn.select_folder(self.folder)

    def start_connection(self):
        conn = IMAPClient(self.host,port=self.port,ssl=self.ssl)
        conn.login(self.user,self.pwd)
        return conn


    def wait_for_message(self):
        try:
            self.conn.idle()
            while True:
                response = self.conn.idle_check(600)
                if response:
                    raise IdleInterrupt
        except IdleInterrupt:
            self.conn.idle_done()
            return self.get_message()


    def get_message(self):
        ids = self.conn.search(criteria='UNSEEN')
        msgs_raw = self.conn.fetch(ids,['RFC822'])
        msgs = []
        for msgid in msgs_raw:
            msgs.append(msgs_raw[msgid]['RFC822'])
        return msgs

if __name__ == '__main__':
    while True:
        try:
            exec(input('>'))
        except BaseException as e:
            print(e)
