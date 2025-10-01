import datetime
import faulthandler
import multiprocessing
import sys
import threading
import time
from tkinter import TclError

import pygtfs
import requests
from flask import Flask, jsonify
from pygtfs import Schedule
from pygtfs import gtfs_entities

import gtfs
from loading import Loading
from stoptripdata import StopTripData
from display import Display

faulthandler.enable()

BART_GTFS: str = 'https://www.bart.gov/dev/schedules/google_transit.zip'
BART_GTFS_FILE: str = "../data/bart-gtfs.zip"
BART_TRIP_UPDATE: str = 'https://api.bart.gov/gtfsrt/tripupdate.aspx'
PLEASANT_HILL_1: str = "C50-1"
PLEASANT_HILL_2: str = "C50-2"

#stop id, StopTripData

watched_stop: str = PLEASANT_HILL_1

schedule: Schedule
stop_list: list[dict[str, str]]
stop_trip_info: dict[str, StopTripData]

app = Flask(__name__)

@app.get("/stop/")
def get_stop():
    return jsonify({
        "stop_id": root.watched_stop
    })

@app.get("/stops/")
def get_stops():
    return jsonify(stop_list)

@app.put("/stop/<string:stop_id>")
def put_stop(stop_id: str = None):
    root.set_watched_stop(stop_id)
    return jsonify({
        "stop_id": root.watched_stop
    })

#@app.post("/update-bart-gtfs/")
#def post_update_bart_gtfs():
#
#    gtfs.update_gtfs_db(schedule)
#    return jsonify(
#        {
#            "updated": True
#        }
#    )

def get_schedule() -> Schedule:
    schedule: Schedule = pygtfs.Schedule("gtfs.sqlite")
    #add_bart_schedule(schedule, True)
    return schedule


def get_stops_info(schedule: Schedule) -> list[dict[str, str]]:
    stop_list: list[dict[str, str]] = list()
    for stop in schedule.stops:
        stop: gtfs_entities.Stop = stop
        stop_list.append(
            {
                "stop_id": stop.stop_id,
                "stop_name": stop.stop_name
            }
        )
    return stop_list


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
        if headsign is None:
            headsign = stop_time.trip.trip_headsign
        #print(f"{stop_time.trip_id} {stop_time.stop_id} {headsign}")
        stop_trip_info[stop_time.stop_id].add(stop_time.trip_id, stop_time.trip.route_id, headsign, arrival_time, departure_time)
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

def app_main():
    app.run(host="0.0.0.0", debug=False, use_reloader=False, use_evalex=False)

def start_loading_info():
    try:
        loading_root: Loading = Loading()
        loading_root.mainloop()
    except TclError as e:
        print(f"{e}", sys.stderr)
        time.sleep(1)

if __name__ == "__main__":

    loading_process = multiprocessing.Process(target=start_loading_info)
    loading_process.start()

    schedule: Schedule = get_schedule()
    gtfs.update_gtfs_db(schedule)
    stop_list: list[dict[str, str]] = get_stops_info(schedule)
    stop_trip_info: dict[str, StopTripData] = default_stop_trip_info(schedule)

    loading_process.terminate()

    #app_main()
    app_thread = threading.Thread(target=app_main)
    app_thread.daemon = True
    app_thread.start()
    while True:
        try:
            root: Display = Display(watched_stop, schedule, stop_trip_info)
            root.mainloop()
        except TclError as e:
            print(f"{e}", sys.stderr)
            time.sleep(1)


