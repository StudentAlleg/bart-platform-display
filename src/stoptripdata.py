import time
from typing import Tuple

import pygtfs.gtfs_entities
from google.transit import gtfs_realtime_pb2

from src.TripData import TripData
from src.UtilTime import UtilTime


class StopTripData:
    stop: pygtfs.gtfs_entities.Stop
    #trip, arrival time
    stop_times: dict[str, TripData]

    def __init__(self, stop: pygtfs.gtfs_entities.Stop):
        self.stop = stop
        self.stop_times = dict()

    def add(self, trip_id:str, route_id: str, headsign: str, arrival_time: int, departure_time):
        self.stop_times[trip_id] = TripData(trip_id, route_id, headsign, arrival_time, departure_time)
    def update(self, trip_id: str, new_arrival: int, new_departure: int) -> None:
        try:
            self.stop_times[trip_id].set_arrival_time(new_arrival)
            self.stop_times[trip_id].set_departure_time(new_departure)
        except KeyError:
            print(f"Unknown trip {trip_id} for station {self.stop.stop_name} {self.stop.stop_id}")

    def get_trip(self, pos: int) -> TripData:
        new_stop_times: dict[str, TripData] = dict(filter(lambda item: item[1].get_departure_time() > UtilTime.now(), self.stop_times.items()))
        return list(new_stop_times.items())[pos][1]

    def get_headsign_trips(self, min_cutoff: int) -> dict[str, list[TripData]]:
        """
        Get a dictionary of a list of TripData by headsign
        :param min_cutoff: how many minutes in the future to be added to this list
        :return:
        """
        headsign_trips: dict[str, list[TripData]] = dict()
        new_stop_times: dict[str, TripData] = dict(filter(lambda item: item[1].get_departure_time() > UtilTime.now(), self.stop_times.items()))
        for _, trip in new_stop_times.items():
            trip: TripData = trip
            if UtilTime.relative_seconds(trip.get_departure_time()) > min_cutoff * 60:
                continue
            if trip.get_headsign() not in headsign_trips:
                headsign_trips[trip.get_headsign()] = list()
            headsign_trips[trip.get_headsign()].append(trip)
        headsign_trips = dict(sorted(headsign_trips.items(), key= lambda item: item[1][0].get_departure_time()))
        return headsign_trips

    def __str__(self) -> str:
        string: str = f"Stop Trip Data {self.stop.stop_id} {self.stop.stop_name}:"
        #for _, data in self.stop_times
        return string

