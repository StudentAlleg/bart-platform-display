import tkinter
from tkinter import ttk, StringVar

import requests
from google.transit import gtfs_realtime_pb2
from pygtfs import Schedule

from routedata import BartRouteData
from stoptripdata import StopTripData
from tripdata import TripData
from utiltime import UtilTime

BART_TRIP_UPDATE: str = 'https://api.bart.gov/gtfsrt/tripupdate.aspx'
FONT: str = "Comic Sans MS"
SMALL_FRONT_SIZE: int = 68
DESCRIPTION_FONT_SIZE: int = 88
ARRIVAL_FONT_SIZE: int = 112

class Display(tkinter.Tk):

    schedule: Schedule
    #todo setter
    watched_stop: str
    stop_trip_info: dict[str, StopTripData]

    headsigns_text: StringVar
    times_text: StringVar
    arrival_text: StringVar
    arrival_desc_text: StringVar

    headsigns_label: tkinter.Label
    times_label: tkinter.Label
    arrival_label: tkinter.Label
    arrival_desc_label: tkinter.Label

    def __init__(self, watched_stop: str, schedule: Schedule, stop_trip_info: dict[str, StopTripData]):
        super().__init__()
        self.watched_stop = watched_stop
        self.schedule = schedule
        self.stop_trip_info = stop_trip_info

        #self.geometry("800x480")
        #self.minsize(800, 480)
        #self.maxsize(800, 480)
        #
        #self.overrideredirect(True)
        self.configure(background="black")
        self.attributes("-fullscreen", True)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, minsize=self.winfo_width()/3)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.headsigns_text = StringVar()
        self.headsigns_label = ttk.Label(self, textvariable=self.headsigns_text, anchor="nw", justify="left", background="black", foreground="red", font=(FONT, SMALL_FRONT_SIZE))
        self.headsigns_label.grid(column=0, row=0, rowspan=2, sticky=tkinter.NW)

        self.times_text = StringVar()
        self.times_label = ttk.Label(self, textvariable=self.times_text, anchor="ne", justify="right", background="black", foreground="red", font=(FONT, SMALL_FRONT_SIZE))
        self.times_label.grid(column=1, row=0, rowspan=2, sticky=tkinter.NE)

        self.arrival_text: StringVar = tkinter.StringVar()
        self.arrival_text.set("ANTIOCH")
        self.arrival_label = ttk.Label(self, textvariable=self.arrival_text, anchor="s", justify="center", background="black", foreground="red", font=(FONT, ARRIVAL_FONT_SIZE), wraplength=self.winfo_width())
        self.arrival_label.grid(column=0, columnspan=2, row=0, sticky=tkinter.S)
        self.arrival_label.grid_remove()


        self.arrival_desc_text: StringVar = StringVar()
        self.arrival_desc_text.set("YL-Line")
        self.arrival_desc_label = ttk.Label(self, textvariable=self.arrival_desc_text, anchor="n", justify="center", background="black", foreground="red", font=(FONT, DESCRIPTION_FONT_SIZE), wraplength=self.winfo_width())
        self.arrival_desc_label.grid(column=0, columnspan=2, row=1, sticky=tkinter.N)
        self.arrival_desc_label.grid_remove()

        self.title("Bart Display")

        self.update_info(True)

    def set_watched_stop(self, watched_stop: str):
        self.watched_stop = watched_stop


    def update_info(self, first: bool = False):
        feed: gtfs_realtime_pb2.FeedMessage = gtfs_realtime_pb2.FeedMessage() # type: ignore

        with requests.get(BART_TRIP_UPDATE, allow_redirects=True) as response:
            feed.ParseFromString(response.content)
            #todo remove
            f = open("../feed.txt", "w")
            f.write(str(feed))
            f.close()
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    if hasattr(entity.trip_update, "stop_time_update"):
                        for trip_update in entity.trip_update.stop_time_update:
                            stop_id: str = trip_update.stop_id
                            #TODO set headsign/add as
                            arrival_time: int = trip_update.arrival.time

                            departure_time: int = trip_update.departure.time
                            if stop_id not in self.stop_trip_info:
                                #update for an unknown station i.e. W40-1
                                continue
                            if entity.id not in (self.stop_trip_info[stop_id]).stop_times:
                                #todo add this new trip in
                                pass
                            self.stop_trip_info[stop_id].update(entity.id, arrival_time, departure_time)
        #display_info(schedule, StopTripInfo)
        print("Updated data")
        if first:
            self.after(250, self.update_display)
        self.after(30*1000, self.update_info, False)

    def update_display(self):
        headsign_trips: dict[str, list[TripData]] = self.stop_trip_info[self.watched_stop].get_headsign_trips(60)
        if len(headsign_trips) > 0:
            _, trips = list(headsign_trips.items())[0]
            if len(trips) > 0:
                trip: TripData = trips[0]
                if trip.get_arrival_time() < UtilTime.now() < trip.get_departure_time():
                    self.arrival_display(trip)
                    self.after(50, self.update_display)
                    return
        self.headsigns_label.grid()
        self.times_label.grid()
        self.arrival_label.grid_remove()
        self.arrival_desc_label.grid_remove()

        working_headsign_text: str = ""
        working_trips_text: str = ""
        for headsign, trips in headsign_trips.items():
            trips: list[TripData] = trips
            working_headsign_text += headsign.upper() + f"\n{BartRouteData.car_lengths(trips[0].route_id)} CAR TRAIN\n"
            for i in range(2):
                try:
                    working_trips_text += str(int(UtilTime.relative_seconds(trips[i].get_departure_time())/60)) + ", "
                except IndexError:
                    working_trips_text += ", "
                    continue
            working_trips_text = working_trips_text.rstrip(", ")
            working_trips_text += " MIN\n\n"
        self.headsigns_text.set(working_headsign_text)
        self.times_text.set(working_trips_text)
        self.after(250, self.update_display)


    def arrival_display(self, trip: TripData):
        self.headsigns_label.grid_remove()
        self.times_label.grid_remove()
        self.arrival_label.grid()
        self.arrival_desc_label.grid()

        now: int = int(UtilTime.now())
        if (now % 2) == 0:
            self.arrival_text.set("")
            self.arrival_desc_text.set("")
            return
        route_id: str = trip.route_id
        self.arrival_text.set(trip.get_headsign().upper())
        self.arrival_desc_text.set(f"{BartRouteData.car_lengths(route_id)}-CAR, {BartRouteData.short_line_color(route_id)}-LINE")

