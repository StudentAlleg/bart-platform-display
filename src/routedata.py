class BartRouteData:
    """
    Extra data that is not included in the BART gtfs data
    """
    @staticmethod
    def short_line_color(route_id: str) -> str:
        if route_id == "1" or route_id == "2":
            return "YL"
        if route_id == "3" or route_id == "4":
            return "OR"
        if route_id == "5" or route_id == "6":
            return  "GR"
        if route_id == "7" or route_id == "8":
            return "RD"
        if route_id == "11" or route_id == "12":
            return "BL"
        if route_id == "19" or route_id == "20":
            return "GRAY"
        return "Unknown Short Line"

    @staticmethod
    def car_lengths(route_id: str) -> int:
        if route_id == "1" or route_id == "2":
            return 9
        if route_id == "19" or route_id == "20":
            return 2
        return 6

