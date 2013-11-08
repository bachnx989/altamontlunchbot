__author__ = 'Simon'

import urllib.request
import re
from datetime import timedelta,date

from bs4 import BeautifulSoup

from LunchBot.datetime_timezone import LocalTime


url = 'http://www.altamontschool.org/calendars/index.aspx?ModuleID=52:53:93' # URL for website calendar page containing relevant data. 52 = letter day, 53 = lunch, 93 = priority

html = urllib.request.urlopen(url)

months = { # This dictionary is required because the website lists months by word whereas datetime.date needs them as ints
    '1' :'Jan',
    '2' :'Feb',
    '3' :'Mar',
    '4' :'Apr',
    '5' :'May',
    '6' :'Jun',
    '7' :'Jul',
    '8' :'Aug',
    '9' :'Sep',
    '10':'Oct',
    '11':'Nov',
    '12':'Dec'
}

def get_month(month_string): # converts month(word) to month(int) e.g. 'Jan' -> 1 or 'Aug' -> 8
    for num in months:
        if re.search(months[num],month_string):
            return int(num)
    else:
        raise RuntimeError("Month string is not a valid month!")


def get_day(day_string): # The <day> part of the soup'd HTML is formatted as [day]. This extracts the day from that in a flexible fashion.
    day = re.findall('\d+',day_string) # Searches day_string (function input) for one or more consecutive digits. Returns a list of all non-overlapping instances it finds
    day_int = int(day[0]) # This assigns day_int to the first item in list 'day', converted to an int (it was a string when it was found.)
    return day_int # returns day_int to the place where the function was called.



def get_calendar_days(html=urllib.request.urlopen('http://www.altamontschool.org/calendars/index.aspx?ModuleID=52:53:93')):
    """


    @rtype : list
    @param html:
    @return:
    """
    raw_soup = BeautifulSoup(html)
    soup_events = raw_soup.find_all('div',class_='inner list')
    calendar_soup = BeautifulSoup(str(soup_events))
    days = calendar_soup.find_all('dl')
    soup_days = [ CalendarDay( str( day ) ) for day in days ]
    return soup_days


class CalendarDay:

    def __init__(self,day_html): # __init__() runs on class instantiation
        """
        Constructs object from raw HTML for a single day
        @param day_html:
        @return:
        """
        self.master_soup = BeautifulSoup(day_html) # Builds a BeautifulSoup object from the day's HTML (HTML is from class_instantiation)


        self.letter = self.make_letter()
        self.lunch = self.make_lunch()
        self.morning_report = self.make_morning_report()
        self.month,self.day = self.make_date()

        self.date = date(LocalTime(-6).date.year,self.month,self.day) # Finishes building the date for the calendar day. Arbitrarily uses the current year.
        if self.date < LocalTime(-6).date: # The current year was just used arbitrarily. If the resulting date is _before_ the current one, the resulting date is next year.
            self.date += timedelta(days=365) # FixMe. Deal with leap-years later. Time is stupid.



    def make_lunch(self):
        """
        Parses raw HTML and returns lunch menu
        @return:
        """
        lunch_soup = BeautifulSoup(
            str(
                self.master_soup.find(
                    'p'
                )
            )
        )
        return lunch_soup.get_text()

    def make_date(self):
        """
        Parses raw HTML and returns month/date
        @return:
        """
        month = self.master_soup.find_all('span',class_='month')
        day = self.master_soup.find_all('span',class_='date')
        raw_date_time = (
            BeautifulSoup(str(month)).get_text(),
            BeautifulSoup(str(day)).get_text()
        )
        return(
            get_month(
                raw_date_time[0]
            ),
            get_day(
                raw_date_time[1]
            )
        )

    def make_letter(self):
        """
        Parses raw HTML to find letter day
        @return:
        """
        try:
            letter = BeautifulSoup(
                str(
                    self.master_soup.find_all(
                        'dd',
                        class_='first-child'
                    )
                )
            )
            return letter.h4.get_text()
        except AttributeError:
            return 'N/A'

    def make_morning_report(self):
        """
        Parses raw HTML for priority excerpt
        @return:
        """
        morning_report = BeautifulSoup(
            str(
                self.master_soup.find(
                    'dd',
                    class_ = 'last-child'
                )
            )
        )

        return BeautifulSoup( str( morning_report.h4 ) ).get_text()

days_list = get_calendar_days(html)

def n_days_later(n):
    global days_list
    delta = timedelta(days=int(n))
    for day in days_list:
        if delta + LocalTime(-6).date == day.date:
            return day
    else:
        return None

def ask_for_parts(in_string):
    current_parts = ''

    if re.search('[Ll]unch',in_string) or re.search('-[Ll]',in_string):
        current_parts += 'l'
    if re.search('[Pp]riority|[Mm]orning [Rr]eport',in_string) or re.search('-[Pp]|-[Mm]',in_string):
        current_parts += 'm'
    if re.search('-[Nn]',in_string):
        current_parts = 'n'
    if in_string == 'help':
        current_parts = 'help'
    return current_parts

def build_response(in_string):
    print(in_string)
    if not re.findall('^[\d]+',in_string): # Search beginning of string for an int. If found, stores it as target_date. If not found, target_date = 0
        target_date = int(
            re.findall(
                '^[\d]+',in_string
            )[0]
        )
    else:
        target_date = 0
    day = n_days_later(target_date)
    if day is None:
        response = 'Date not in school calendar'
    else:
        response = str(day.date)+'\n'+day.letter
    parts = ask_for_parts(in_string)
    if 'l' in parts and not day is None:
        response += '\n'+day.lunch
    if 'm' in parts and not day is None:
        response += '\n'+day.morning_report
    if not 'l' in parts and not 'm' in parts and not 'n' in parts and not day is None:
        response += '\n'+day.lunch+'\n'+day.morning_report
    if parts == 'help':
        response = """There 2 ways to use lunchbot: general and targeted.

        General: Text lunchbot anything that _isn't_ a keyword defined in targeted.
        Lunchbot will respond with today's lunch, letter day, and priority.

        Targeted: If the first line of your text is a number, lunchbot will respond with info about that many dates into the future. This can also be used with commands.
        You can also get partial responses by passing lunchbot commands! -l for lunch, -m or -p for priority, -n for none (Only letter/date).
        Lunchbot also interprets 'lunch', 'priority' and 'morning report' the same way as it does commands.
        Text 'help' to get this response.
        Lunchbot written, implemented, and (selectively) maintained by Simon."""

    return response




if __name__ == '__main__':
    while True:
        i = input('pseudo text attachment')
        print(
            build_response(i)
        )


#Helpfile:

#Any string that doesn't have the following in it somewhere
#will get everything in response. 1st line should be int(days from now) to query. If gibberish, assume 0.

# Every reply includes date and letter-day
# if Lunch,lunch,-l, -L then Lunch is included
# if Priority,priority,Morning Report, morting Report, Morning report, morning report, -p,-P, -m or -M then Priority is included.

# Lunchbot takes no responsibility for utterly false information. Lunchbot is not a substitute for professional medical advice.