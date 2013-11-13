import smtplib



class SMTP_Connection(object):
    def __init__(self,host='smtp.gmail.com',user='altamontlunchbot@gmail.com',pwd='lunchbotpassword',port=465,ssl=True):
        """
        Constructs an SMTP connection class to send messages
        @param user:
        @param pwd:
        @param host:
        @param port:
        @param ssl:
        @return:
        """
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.ssl = ssl
        self.start_smtp()

    def start_smtp(self):
        if self.ssl:
            conn = smtplib.SMTP_SSL(self.host,port=self.port)
        else:
            conn = smtplib.SMTP(self.host,port=self.port)
        conn.login(self.user,self.pwd)
        self.conn = conn

    def send_smtp(self,to,msg): # Tries to send _msg_ to _to_. Tries to open a connection if the server isn't connected for some reason.
        try:
            self.conn.sendmail(self.user,to,msg)
        except smtplib.SMTPServerDisconnected: # SMTPServerDisconnected is raised if the server is not open for some reason (never started or timed out).
            print('smtp connection timed out! restarting!')
            self.start_smtp()
            self.send_smtp(to,msg)
