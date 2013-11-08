__author__ = 'Simon'

# This figures out what time it is in Alabama, regardless of where the script is hosted.
# It really shouldn't have to be this long, but the datetime module is stupid.

from datetime import datetime,timedelta

class LocalTime:

    def __init__(self,timezone=-6):
        self.timezone = timedelta(hours=timezone)
        self.start_dst = datetime(year=2010,month=3,day=10,hour=2)
        self.end_dst = datetime(year=2010,month=11,day=3,hour=2)

    def apply_dst(self):
        if self.start_dst.replace(year=datetime.now().year) < datetime.now() < self.end_dst.replace(year=datetime.now().year):
            return timedelta(hours=1)
        else:
            return timedelta(hours=0)

    def get_datetime(self):
        current_datetime = datetime.utcnow()+self.apply_dst()+self.timezone
        return current_datetime
    def get_date(self):
        current_date = self.get_datetime().date() # todo Leap years might be a problem here. Figure out a way to deal with that.
        return current_date
    time = property(get_datetime)
    date = property(get_date)

    def __str__(self):
        return(
            str(
                self.time.date()
            )
        )

    def n_days_later(self,n):
        delta = timedelta(days=int(n))
        new_date = delta + self.date
        return new_date


if __name__ == '__main__':
    while True:
        in_tz = input("What timezone?")
        x = LocalTime(int(in_tz)).date
        print(type(x))
        print(x)