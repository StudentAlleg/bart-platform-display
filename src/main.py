import datetime
import faulthandler
import time
import tkinter
from tkinter import ttk, StringVar

import pygtfs
import requests
from google.transit import gtfs_realtime_pb2
from pygtfs import Schedule
from pygtfs import gtfs_entities
from pygtfs.gtfs_entities import Trip

from src.stoptripdata import StopTripData
from src.TripData import TripData
from src.UtilTime import UtilTime
from src.display import Display

faulthandler.enable()

BART_GTFS: str = 'https://www.bart.gov/dev/schedules/google_transit.zip'
BART_GTFS_FILE: str = "../data/bart-gtfs.zip"
BART_TRIP_UPDATE: str = 'https://api.bart.gov/gtfsrt/tripupdate.aspx'
PLEASANT_HILL_1: str = "C50-1"
PLEASANT_HILL_2: str = "C50-2"

#stop id, StopTripData


watched_stop: str = PLEASANT_HILL_1

def get_schedule() -> Schedule:
    schedule: Schedule = pygtfs.Schedule(":memory:")
    add_bart_schedule(schedule)
    return schedule

def default_stop_trip_info(schedule: Schedule) -> dict[str, StopTripData]:
    stop_trip_info: dict[str, StopTripData] = dict()
    day_start: int = int(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    for stop in schedule.stops:
        stop: pygtfs.gtfs_entities.StopTime = stop
        stop_trip_info[stop.stop_id] = StopTripData(stop)
    for stop_time in schedule.stop_times:
        stop_time: pygtfs.gtfs_entities.StopTime = stop_time
        arrival_time_delta: datetime.timedelta = stop_time.arrival_time
        departure_time_delta: datetime.timedelta = stop_time.departure_time
        arrival_time: int = int(arrival_time_delta.total_seconds() + day_start)
        departure_time: int = int(departure_time_delta.total_seconds() + day_start)
        headsign: str = stop_time.stop_headsign
        if (headsign is None):
            headsign = stop_time.trip.trip_headsign
        print(f"{stop_time.trip_id} {stop_time.stop_id} {headsign}")
        stop_trip_info[stop_time.stop_id].add(stop_time.trip_id, headsign, arrival_time, departure_time)
    return stop_trip_info

def add_bart_schedule(schedule: Schedule, fetch_from_url: bool = False) -> None:
    """
    Updates and adds the bart schedule
    @:param fetch_from_url whether to download the current gtfs or just use last downloaded schedule
    """
    #update from bart's gtfs .zip
    if fetch_from_url:
        with requests.get(BART_GTFS) as response:
            if response.status_code == 200:
                with open(BART_GTFS_FILE, "wb") as file:
                    file.write(response.content)
    pygtfs.append_feed(schedule, BART_GTFS_FILE)

if __name__ == "__main__":
    schedule: Schedule = get_schedule()
    stop_trip_info: dict[str, StopTripData] = default_stop_trip_info(schedule)
    root: Display = Display(watched_stop, schedule, stop_trip_info)
    root.mainloop()

