class TripData():
    trip_id: str
    route_id: str
    headsign: str
    arrival_time: int
    departure_time: int

    def __init__(self, trip_id, route_id, headsign = "Unknown Headsign", arrival_time = -1, departure_time = -1):
        self.trip_id = trip_id
        self.route_id = route_id
        self.headsign = headsign
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def get_trip_id(self) -> str:
        return self.trip_id

    def get_headsign(self) -> str:
        return self.headsign

    def set_arrival_time(self, arrival_time: int) -> None:
        self.arrival_time = arrival_time

    def get_arrival_time(self) -> int:
        return self.arrival_time

    def set_departure_time(self, departure_time: int) -> None:
        self.departure_time = departure_time

    def get_departure_time(self) -> int:
        return self.departure_time