import requests
from pygtfs import Schedule
import pygtfs
BART_GTFS: str = 'https://www.bart.gov/dev/schedules/google_transit.zip'
BART_GTFS_FILE: str = "../data/bart-gtfs.zip"

def update_gtfs_db(schedule: Schedule):
    """
       Updates and adds the bart schedule
       """
    #update from bart's gtfs .zip
    with requests.get(BART_GTFS) as response:
        if response.status_code == 200:
            with open(BART_GTFS_FILE, "wb") as file:
                file.write(response.content)
    pygtfs.append_feed(schedule, BART_GTFS_FILE)