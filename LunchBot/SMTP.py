import smtplib

class SMTP_Connection(smtplib.SMTP_SSL):

    def __init__(self,host,user,pwd,port=465):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        for i in range(5):
            try:
                super(SMTP_Connection, self).__init__(self.host,port=self.port)
                break
            except smtplib.SMTPConnectError:
                print("Error during smtp connection! Trying again (try {})"%str(i+1))
                if i == 4:
                    raise RuntimeError("SMTP Connection refused 5 consecutive times.")


    def __enter__(self):
        print("Opening SMTP Connection to {} on port {}"%self.host,self.port)
        return self

    def login(self):
        try:
            super(SMTP_Connection, self).login(self.user,self.pwd)
        except smtplib.SMTPAuthenticationError:
            print("Server refused login credentials!")


    def sendmail(self,to,msg):
        print("Sending message to {}"%to)
        for i in range(5):
            try:
                super(SMTP_Connection, self).sendmail(self.user,to,msg)
                break
            except smtplib.SMTPAuthenticationError:
                print("Not in [AUTH] (or something more sinister). Trying to log in again.")
                self.login()
            except smtplib.SMTPRecipientsRefused:
                print("Invalid recipient address!")
            except smtplib.SMTPDataError:
                print("Data was refused by server!")
            except smtplib.SMTPResponseException as exception:
                print("Response Exception:\n"+str(exception))

    def __exit__(self,type_,val,tb):
        print("Closing SMTP Connection to {} on port {}"%self.host,self.port)
        if type_ == smtplib.SMTPException:
            print("Unhandled Exception")
        self.close()
        return True



with SMTP_Connection("smtp.gmail.com","altamontlunchbot@gmail.com","lunchbotpassword") as conn:
    conn.login()


