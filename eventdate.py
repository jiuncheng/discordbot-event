import datetime
import pytz
from dateutil import tz

tz = tz.gettz('Asia/Kuala_Lumpur')
localtz = pytz.timezone("Asia/Kuala_Lumpur")

class EventDate:

    dtEvent: datetime

    def __init__(self, dtEvent: str=None, jsonDate: str=None):
        if jsonDate is not None:
            self.dtEvent = self.insertJsonDate(jsonDate)
        elif dtEvent is not None:
            self.dtEvent = self.insertDate(dtEvent)
            self.convertToUtc()
            self.convertDateToTimezone()

    def insertJsonDate(self, jsonDate):
        return datetime.datetime.strptime(jsonDate, '%Y-%m-%d %H:%M:%S%z')

    def convertToUtc(self):
        local = localtz.localize(self.dtEvent, is_dst=None)
        self.dtEvent = local.astimezone(pytz.utc)

    def convertDateToTimezone(self):
        #localtime = pytz.localize(self.dtEvent, is_dst=None).astimezone(tz)
        localtime = self.dtEvent.astimezone(tz)
        self.dtEvent = localtime

    def insertDate(self, dtEvent: str):
        if "/" in dtEvent and "," in dtEvent and ":" in dtEvent:
            date = dtEvent.split("/")
            year = date[2].split(",")
            time = date[2].split(",")
            time = time[1].split(":")
            return datetime.datetime(int(year[0]), int(date[1]), int(date[0]), int(time[0]), int(time[1]))

        elif ("am" in dtEvent or "AM" in dtEvent or "Am" in dtEvent or "aM" in dtEvent) and ":" in dtEvent:
            time = dtEvent.split(":")
            time2 = time[1][:-2]
            nowDate = datetime.datetime.now().replace(second=0)
            newDate = nowDate.strftime("%Y-%m-%d")
            newDate2 = datetime.datetime.strptime((newDate + " " + time[0] + ":" + time2 + "AM"), "%Y-%m-%d %I:%M%p")
            return newDate2

        elif("pm" in dtEvent or "PM" in dtEvent or "Pm" in dtEvent or "pM" in dtEvent) and ":" in dtEvent:
            time = dtEvent.split(":")
            time2 = time[1][:-2]
            nowDate = datetime.datetime.now().replace(second=0)
            newDate = nowDate.strftime("%Y-%m-%d")
            newDate2 = datetime.datetime.strptime((newDate + " " + time[0] + ":" + time2 + "PM"), "%Y-%m-%d %I:%M%p")
            return newDate2

        elif ":" in dtEvent:
            time = dtEvent.split(":")
            nowDate = datetime.datetime.now().replace(second=0)
            return nowDate.replace(hour=int(time[0]), minute=int(time[1]), microsecond=0)

        elif dtEvent[-1] == "h":
            time = dtEvent[:-1]
            return (datetime.datetime.now().replace(second=0) + datetime.timedelta(hours=int(time))).replace(microsecond=0)

        elif len(dtEvent) == 4:
            time1 = dtEvent[:2]
            time2 = dtEvent[-2:]
            nowDate = datetime.datetime.now().replace(second=0)
            return nowDate.replace(hour=int(time1), minute=int(time2), microsecond=0)
            

    def getCurrentDT(self):
        time = datetime.datetime.utcnow().replace(microsecond=0)
        localtime = pytz.utc.localize(time, is_dst=None).astimezone(tz)
        return localtime

    def replaceDate(self):
        now = self.dtEvent.replace(hour=18, minute=33)
        self.dtEvent = now
        return

    def calcDiff(self):
        print(self.dtEvent)
        print(self.getCurrentDT())
        diff = self.dtEvent - self.getCurrentDT()
        diffSeconds = int(diff.total_seconds())
        return diffSeconds
    
    def checkValidEventDate(self):
        seconds = self.calcDiff()
        print(seconds)
        return seconds > 0

    def displayDate(self):
        if self.dtEvent.date() == datetime.datetime.now().date():
            return "Today, " + self.dtEvent.strftime("%d %b %I:%M%p")
        else:
            return self.dtEvent.strftime("%a, %d %b %I:%M%p")

    def displayTime(self):
        if self.dtEvent.date() == datetime.datetime.now().date():
            return "Today, " + self.dtEvent.strftime("%I:%M%p")
        else:
            return self.dtEvent.strftime("%a, %d %b %I:%M%p")

    def displayDuration(self):
        diff = (self.dtEvent - self.getCurrentDT())
        sec = int(diff.total_seconds())
        td = datetime.timedelta(seconds=sec)

        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if sec > (60 * 60 * 24):
            return str(days) + " Days"

        elif sec >= (60 * 60):
            return str(hours) + " Hours " + str(minutes + 1) + " Mins"

        else:
            return str(minutes + 1) + " Mins"
