__author__ = 'Simon'

import re,sys,traceback

class TracebackDecorator(object):
    def __init__(self,func):
        self.func = func

    def process_tb(self,file=None):
        traceback.print_exc(file=file)

    def __call__(self,*args):
        try:
            self.func(*args)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)

help_text = """There 2 ways to use lunchbot: general and targeted.

        General: Text lunchbot anything that _isn't_ a keyword defined in targeted.
        Lunchbot will respond with today's lunch, letter day, and priority.

        Targeted: If the first line of your text is a number, lunchbot will respond with info about that many dates into the future. This can also be used with commands.
        You can also get partial responses by passing lunchbot commands! -l for lunch, -m or -p for priority, -n for none (Only letter/date).
        Lunchbot also interprets 'lunch', 'priority' and 'morning report' the same way as it does commands.
        Text 'help' to get this response.
        Lunchbot written, implemented, and (selectively) maintained by Simon."""

from LunchBot import IMAP,SMTP,scrape
from LunchBot.datetime_timezone import LocalTime
from LunchBot.Mail import Mail
import urllib.request

calendar_data = scrape.get_calendar_days()

class ScheduleException(Exception):

    def __init__(self):
        super(ScheduleException, self).__init__()

class TextMessage(Mail):

    def __init__(self,mail_string):
        if type(mail_string) == type([]) and len(mail_string) == 1:
            mail_string = mail_string[0]
        super(TextMessage, self).__init__(mail_string)
        self.sender = self.mail["From"]
        self.text = self.get_text()
        self.date,self.flags = self.parse_message()


    def parse_message(self): # todo: Add schedule support to message parsing
        try:
            schedule = re.findall('(?<={)(?:.+?,){6}(?=})',self.text)
            if len(schedule) is 1:
                raise ScheduleException
            flags = set()
            date_int = re.findall('(?<=^)[\d]+',self.text)
            if not date_int:
                date = LocalTime().n_days_later(0)
            else:
                date = LocalTime().n_days_later(int(date_int[0]))


            if re.search('[Ll]unch',self.text) or re.search('-[Ll]',self.text): # User asked for lunch
                flags.add('lunch')
            if re.search('[Pp]riority|[Mm]orning [Rr]eport',self.text) or re.search('-[Pp]|-[Mm]',self.text): # User asked for Morning Report
                flags.add('priority')
            if re.search('-[Nn]',self.text):
                flags.add('day')
            if re.search('^[Hh]elp$|-[Hh]',self.text):
                flags.add('help')
            if not flags:
                print('not flags!')
                flags.add('day')
                flags.add('lunch')
                flags.add('priority')
            print(date)
            return date,flags
        except ScheduleException:
            pass # todo Finish and integrate schedule code here

    def build_reply(self):

        for calendar_day in calendar_data:
            if calendar_day.date == self.date:
                break
        else:
            self.date = None
            self.day = None
            self.priority = None
            self.lunch = None
            return 'Date not in calendar.'
        self.date = calendar_day.date
        self.day = calendar_day.letter
        self.priority = calendar_day.morning_report
        self.lunch = calendar_day.lunch

        #todo: Stick this somewhere to build non-schedule messages.

        reply = ''
        if 'help' in self.flags:
            return help_text
        if 'day' in self.flags:
            reply += calendar_day.letter+'\n'
        if 'priority' in self.flags:
            reply += calendar_day.morning_report+'\n'
        if 'lunch' in self.flags:
            reply += calendar_day.lunch+'\n'
        return reply


@TracebackDecorator
def main():
    calendar_url = 'http://www.altamontschool.org/calendars/index.aspx?ModuleID=52:53:93'
    global calendar_data
    calendar_data = scrape.get_calendar_days(urllib.request.urlopen(calendar_url))
    print("Calendar Scrape Finished")
    IMAP_conn = IMAP.IMAP_Connection()
    print("IMAP Connection started!")
    SMTP_conn = SMTP.SMTP_Connection()
    print("SMTP Connection started!")
    # note Main Loop

    while True:
        msgs_raw = IMAP_conn.wait_for_message(SMTP_conn) # SMTP_conn is passed as an arg so that it gets noop()'d when IMAP_conn idles.
        if type(msgs_raw) == str:
            msgs_raw = [msgs_raw]
        for msg_raw in msgs_raw:
            msg = TextMessage(msg_raw)
            print('Message Received!\n'+msg.text)
            reply = msg.build_reply()
            SMTP_conn.send_smtp(msg.sender,reply)




if __name__ == '__main__':
    main()

