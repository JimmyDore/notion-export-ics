
import json
from datetime import datetime

from icalendar import Calendar, Event
from notion.client import NotionClient
from notion.collection import CalendarView
from notion.block import BasicBlock
from notion.user import User


# Hack some representation stuff into notion-py

BasicBlock.__repr__ = BasicBlock.__str__ = lambda self: self.title
User.__repr__ = User.__str__ = lambda self: self.given_name or self.family_name


def get_ical(client, calendar_url):
    calendar = client.get_block(calendar_url)
    for view in calendar.views:
        if isinstance(view, CalendarView):
            calendar_view = view
            break
    else:
        raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")

    collection = calendar_view.collection

    cv = client.get_collection_view(calendar_url)
    events_list = {}
    for row in cv.collection.get_rows():
        try:
            date = row.due_date.start
        except:
            print(f"no due date")
            continue

        status = row.status
        print(status)
        if "Done" in status:
            print(f"task already done")
            continue

        label = row.label

        title = row.title
        url = row.get_browseable_url()
        
        events_list.setdefault(label,[]).append({
            "title" : title,
            "url" : url,
            "date" : date
        })

    cal_dict = {}    
    for label, events in events_list.items():
        cal = Calendar()
        cal.add("summary", "Imported from Notion, via notion-export-ics.")
        cal.add('version', '2.0')

        for e in events:
            date = e["date"]
            title = e["title"]
            url = e["url"]

            clean_props = {'NAME': title}
        
            # Put in ICS file
            event = Event()
            event.add('dtstart', date)
            event.add('dtend', date)
            event.add('summary', title)

            desc = url + '\n\n'
            event.add('description', desc)
            cal.add_component(event)

        cal_dict[label] = cal

    return cal_dict

