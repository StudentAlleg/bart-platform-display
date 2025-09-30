import json

import requests
import tkinter
from tkinter import ttk, StringVar
from tkinter.messagebox import showwarning, showerror


class Frontend(tkinter.Tk):
    stop_list: list[dict[str, str]]

    ip_label: ttk.Label
    ip_var: StringVar
    ip_box: ttk.Entry

    port_label: ttk.Label
    port_var: StringVar
    port_box: ttk.Entry

    refresh_button: ttk.Button

    stop_id_var: StringVar
    stop_selector_box: ttk.Combobox

    submit_button: ttk.Button
    refetch_button: ttk.Button

    def __init__(self):
        super().__init__()

        self.ip_label = ttk.Label(text="ip:")
        self.ip_label.grid(column=0, row=0)

        self.ip_var = StringVar()
        self.ip_var.set("http://display")
        self.ip_box = ttk.Entry(self, textvariable=self.ip_var)
        self.ip_box.grid(column=1, row=0)

        self.port_label = ttk.Label(text="port:")
        self.port_label.grid(column=2, row=0)

        self.port_var = StringVar()
        self.port_var.set("5000")
        self.port_box = ttk.Entry(self, textvariable=self.port_var)
        self.port_box.grid(column=3, row=0)

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh)
        self.refresh_button.grid(column=0, row=1, columnspan=4, sticky=tkinter.W)

        self.stop_id_var = StringVar()
        self.stop_selector_box = ttk.Combobox(self, textvariable=self.stop_id_var, state="readonly", width=40)
        self.stop_selector_box.grid(column=0, row=2, columnspan=4, sticky=tkinter.W)

        self.submit_button = ttk.Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(column=0, row=3, columnspan=4, sticky=tkinter.W)

        #self.refetch_button = ttk.Button(self, text="Refetch GTFS Data", command=self.refetch)
        #self.refetch_button.grid(column=0, row=4, columnspan=4, sticky=tkinter.W)

        self.title("Bart Display Controller")

        self.refresh()

    def get_url(self, path = ""):
        ip_address: str = f"{self.ip_var.get()}:{self.port_var.get()}/"
        if path == "":
            return ip_address
        return ip_address + path + "/"

    def refresh(self):
        try:
            response: requests.Response = requests.get(self.get_url("stops"))
            if response.status_code != 200:
                showwarning(f"Error: {response.status_code}", f"{response.content}")
            self.stop_list = json.loads(response.content)

            stop_id_response: requests.Response = requests.get(self.get_url("stop"))
            if stop_id_response.status_code != 200:
                showwarning(f"Error: {stop_id_response.status_code}", f"{stop_id_response.content}")

            watched_stop_id: str = json.loads(stop_id_response.content)["stop_id"]

            stop_selector_values: list[str] = list()
            stop_selected: str = "UNKNOWN"
            for stop_info in self.stop_list:
                selector_val: str = f"{stop_info['stop_id']} ({stop_info['stop_name']})"
                stop_selector_values.append(selector_val)
                if stop_info["stop_id"] == watched_stop_id:
                    stop_selected = selector_val

            self.stop_selector_box["values"] = stop_selector_values
            self.stop_id_var.set(stop_selected)
            self.stop_selector_box.set(stop_selected)
        except Exception as e:
            showerror("Error", str(e))


    def submit(self):
        try:
            response: requests.Response = requests.put(self.get_url("stop") + self.get_stop_id_from_selector())
            if response.status_code != 200:
                showwarning(f"Error: {response.status_code}", f"{response.content}")
        except Exception as e:
            showerror("Error", str(e))


    def get_stop_id_from_selector(self) -> str:
        return self.stop_id_var.get().split(" (")[0]

    def refetch(self):
        response: requests.Response = requests.post(self.get_url("update-bart-gtfs"))
        if response.status_code != 200:
            showwarning(f"Error: {response.status_code}", f"{response.content}")
        self.stop_list = json.loads(response.content)



if __name__ == "__main__":
    #response: requests.Response = requests.put("http://127.0.0.1:5000/stop/C50-2")
    #print(response.status_code)
    #print(response.content)
    root = Frontend()
    root.grid()
    root.mainloop()
