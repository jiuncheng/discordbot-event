import json, random
import eventdate
from eventdate import EventDate

class Events:

    events: list = []

    def __init__(self):
        self.events = self.getEvents()

    def getEvents(self):
        with open('event.json', 'r') as f:
            events = json.load(f)
            return events

    def createEvent(self, title: str, dateTime: str, creator: dict):
        self.events = self.getEvents()
        date = EventDate(dateTime)
        if not date.checkValidEventDate():
            return None

        eventDate = date.dtEvent    
        createDate = date.getCurrentDT()
        id = self.generateEventID()

        event = {
            'id': id,
            'title': title,
            'status': "ongoing",
            'eventDate': eventDate,
            'createDate': createDate,
            'creator': creator,
            'going': [creator]
        }
        self.events.append(event)
        self.saveEvents(self.events)
        return self.getSingleEvent(id)

    def getSingleEvent(self, id: int):
        self.events = self.getEvents()
        for event in self.events:
            if event['id'] == id:
                return event
        return None

    def generateEventID(self):
        id = random.randint(100, 199)
        while not self.checkAvailableID(id):
            id = random.randint(100, 199)
        return id

    def checkAvailableID(self, id: int):
        self.events = self.getEvents()
        for event in self.events:
            if event['id'] == id:
                return False
        return True

    def displayGoingMembers(self, members):
        i = 0
        data = ""
        if len(members) >= 1:
            for member in members:
                i += 1
                id = str(member['id'])
                id = '<@{}>'.format(id)
                data += "{}. {}\n".format(i, id)
        else:
            data = f"""No one is going. <:pepehands:447648996404625409>"""
        return data

    def saveEvents(self, events):
        with open('event.json', 'w') as f:
            json.dump(events, f, default=str)

    def getEventsInfo(self):
        self.events = self.getEvents()
        i = 0
        data = ""

        for event in self.events:
            i += 1

            eventDate = EventDate(jsonDate=event['eventDate'])
            createDate = eventDate.getCurrentDT()

            data += "{}. **{}** at {} by {}\n".format(i, event['title'], eventDate.displayTime(), event['creator']['name'])
        return data

    def deleteEvent(self, id: int):
        events = self.getEvents()
        i = 0
        for event in events:
            if not event['id'] == id:
                i += 1
            else:
                break
        del events[i]
        self.saveEvents(events)
