import tkinter
from tkinter import ttk, StringVar

import requests
from google.transit import gtfs_realtime_pb2
from pygtfs import Schedule

from routedata import BartRouteData
from stoptripdata import StopTripData
from tripdata import TripData
from utiltime import UtilTime

FONT: str = "Helvetica" #"Comic Sans MS"
FONT_SIZE: int = 56

class Loading(tkinter.Tk):

    loading_text: StringVar
    loading_label: tkinter.Label

    start_time: int


    def __init__(self):
        super().__init__()

        self.start_time = UtilTime.now()

        self.geometry("1024x768")
        self.minsize(1024, 768)
        self.maxsize(1024, 768)

        #self.overrideredirect(True)
        self.configure(background="black")
        self.attributes("-fullscreen", True)
        self.attributes("-zoomed", True)
        self.config(cursor="none")

        self.loading_text = StringVar()
        self.loading_label = ttk.Label(self, textvariable=self.loading_text, anchor="nw", justify="left", background="black", foreground="red", font=(FONT, FONT_SIZE))
        self.loading_label.grid(column=0, row=0, rowspan=2, sticky=tkinter.NW)

        self.title("Loading")

        self.update_display()


    def update_display(self):
        self.loading_text.set(f"Loading... {abs(UtilTime.relative_seconds(self.start_time))}s elapsed")
        self.after(250, self.update_display)

