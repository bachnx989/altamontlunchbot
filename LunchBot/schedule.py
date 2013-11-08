__author__ = 'Simon'

import re,sys,datetime

class Schedule(object): #Bullds a schedule object

    def __init__(self,data):
        """
        data is a string 7 lines long. Consists of period \n elective_a | elective_b \n period etc...
        """
        self.schedule = self.read_data(data)

    def read_data(self,data):
        data = re.findall('(?<={).+(?=})',data) # Find all instances of text between { }s
        raw_list = data[0].split(',')
        return(
            [
            re.findall('(?:^|\|)(.+?)(?=$|\|)',period) for period in raw_list
        ]
        )

    def get_class(self,day,period):
        day_dict = {
            'a day':0,
            'b day':1,
            'c day':2,
            'd day':3,
            'e day':4,
            'f day':5,
            'g day':6
        }

        if type(day) == 'string': # This converts the letter day to an int if it came from scrape.
            day = day_dict[day.lower()]
        p = self.schedule[(-day+period)%7]

        if len(p) == 1:
            return p[0]
        else:
            if ((-day+period)%7)%2 == period%2: # Pick correct elective. If the elective was period 7 on A day, this thinks of it as period 1 on b day
                return p[0]
            else:
                return p[1]

    def build_dump(self):
        raw_list = []
        for period in self.schedule:
            if len(period) == 1:
                raw_list.append(period[0])
            else:
                raw_list.append(

                    period[0]+'|'+period[1]
                )
        raw_schedule = ','.join(raw_list)
        raw_text = '{'+self.user+'}'+'{'+raw_schedule+'}'
        return raw_text







#try:
#    f = open('schedules.txt','r')
#    pickle.load(f)
#except FileNotFoundError:
#    schedules = {}

user_list = []

def add_to_schedule(schedule_object):
    user_dict[schedule_object.user]=schedule_object

def get_schedule_data(user,day,period):
    try:
        data = user_dict[user].get_class(day,period)
    except ValueError:
        data = 'Schedule not in LunchBot database!'
    return data

def save_schedule(schedule_list):
    f = open('schedules.txt','w')
    f.write(pickle.dumps(schedule_list))
    f.close()


class User(object):


    def __init__(self,*args):
        if len(args) == 2:
            self.user = args[0]
            self.schedule_text = args[1]
        else:
            parts = re.findall('(?<={).+(?=})',args[0])
            self.user = parts[0]
            self.schedule_text = parts[1]
        self.schedule = Schedule(self.schedule_text)
        user_dict[self.user]=self

    def build_schedule(self):
        raw_list = self.schedule_text.split(',')
        return(
            re.findall('(?:^|\|)(.+?)(?=$|\|)',period) for period in raw_list
        )

    def build_dump(self):
        raw_list = []
        for period in self.schedule:
            if len(period) == 1:
                raw_list.append(period[0])
            else:
                raw_list.append(

                    period[0]+'|'+period[1]
                )
        raw_schedule = ','.join(raw_list)
        raw_text = '['+self.user+']'+'['+raw_schedule+']'
        return raw_text
    dump_text = property(build_dump)

def build_from_file():

    try:
        saved_schedules = open('schedules.txt','r')
        raw_text = saved_schedules.read()
        saved_schedules.close()
    except FileNotFoundError: # Called if schedules.txt doesn't exist
        return {}
    users_raw = raw_text.split('\n')
    print(raw_text)
    user_dict = {}
    for raw in users_raw:
        if not re.findall('\w',raw):
            continue
        user_object = User(raw)
        user_dict[user_object.user] = user_object
    return user_dict
user_dict = {}
def dump_to_file():
    try:
        dump_file = open('schedules.txt','w')
        for i in user_dict:
            dump_file.write(user_dict[i].dump_text)
            dump_file.write('\n')
        dump_file.close()
        return True
    except FileNotFoundError:
        return False


if __name__ == '__main__':
    while True:
        try:
            exec(input('>'))
        except Exception as e:
            print(e)



