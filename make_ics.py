import json
from notion.client import NotionClient
from notion_ics import get_ical
import sys

with open(sys.argv[1]) as f:
    settings = json.load(f)

client = NotionClient(settings['token'], monitor=False)
cal_dict = get_ical(client, settings['calendar_url'])

for label,cal in cal_dict.items():
    with open(f'{label}.ics', 'wb') as f:
        f.write(cal.to_ical())
        f.close()
